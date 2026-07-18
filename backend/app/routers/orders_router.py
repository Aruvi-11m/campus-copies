from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from .. import models, schemas, deps, database, pricing, storage
from datetime import datetime, timezone
import io
from pypdf import PdfReader
import uuid

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/calculate-cost", response_model=schemas.CostPreview)
def preview_cost(
    pages: int,
    copies: int,
    print_type: str,
    color: str,
    binding: str,
    db: Session = Depends(database.get_db)
):
    pricing_settings = db.query(models.PricingSettings).first()
    if not pricing_settings:
        raise HTTPException(status_code=500, detail="Pricing settings not configured")
    
    cost_data = pricing.calculate_cost(pages, copies, print_type, color, binding, pricing_settings)
    return {
        "pages": pages,
        "copies": copies,
        "print_type": print_type,
        "color": color,
        "binding": binding,
        **cost_data
    }

@router.post("", response_model=schemas.OrderResponse)
def create_order(
    print_type: str = Form(...),
    color: str = Form(...),
    binding: str = Form(...),
    copies: int = Form(1),
    notes: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(deps.get_current_student)
):
    # Verify file is a PDF
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read PDF to count pages
    try:
        content = file.file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        pages = len(pdf_reader.pages)
        file.file.seek(0) # reset pointer for saving
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid PDF file")

    # Save file
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = storage.save_file(file, unique_filename)

    # Calculate authoritative cost
    pricing_settings = db.query(models.PricingSettings).first()
    cost_data = pricing.calculate_cost(pages, copies, print_type, color, binding, pricing_settings)

    # Generate Order Number
    # Simple logic for this MVP: CC-000000 format
    last_order = db.query(models.Order).order_by(models.Order.id.desc()).first()
    next_id = last_order.id + 1 if last_order else 1
    order_number = f"CC-{next_id:06d}"

    new_order = models.Order(
        order_number=order_number,
        student_id=current_student.id,
        original_filename=file.filename,
        file_path=file_path,
        pages=pages,
        copies=copies,
        print_type=print_type,
        color=color,
        binding=binding,
        notes=notes,
        printing_cost=cost_data["printing_cost"],
        binding_cost=cost_data["binding_cost"],
        gst_amount=cost_data["gst_amount"],
        grand_total=cost_data["grand_total"],
        status="PENDING_PAYMENT"
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Audit Log
    db.add(models.AuditLog(
        user_type="student",
        user_identifier=current_student.mobile_number,
        action="CREATE_ORDER",
        details=f"Order {order_number} created"
    ))
    db.commit()
    
    return new_order

@router.post("/{order_id}/payment", response_model=schemas.OrderResponse)
def submit_payment(
    order_id: int,
    payment_transaction_id: str = Form(...),
    screenshot: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(deps.get_current_student)
):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.student_id == current_student.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "PENDING_PAYMENT":
        raise HTTPException(status_code=400, detail="Order is not pending payment")

    unique_filename = f"payment_{uuid.uuid4()}_{screenshot.filename}"
    file_path = storage.save_file(screenshot, unique_filename)

    order.payment_transaction_id = payment_transaction_id
    order.payment_screenshot_path = file_path
    order.status = "PAYMENT_VERIFICATION"
    order.payment_submitted_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(order)
    return order

@router.get("", response_model=list[schemas.OrderResponse])
def get_my_orders(
    db: Session = Depends(database.get_db),
    current_student: models.Student = Depends(deps.get_current_student)
):
    return db.query(models.Order).filter(models.Order.student_id == current_student.id).order_by(models.Order.created_at.desc()).all()
