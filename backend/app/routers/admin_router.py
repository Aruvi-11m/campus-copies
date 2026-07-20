from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, deps, database
from datetime import datetime, timezone
import random

router = APIRouter(prefix="/admin", tags=["admin"])

# Settings
@router.get("/pricing", response_model=schemas.PricingSettingsResponse)
def get_pricing_settings(db: Session = Depends(database.get_db), current_admin: models.Admin = Depends(deps.get_current_admin)):
    settings = db.query(models.PricingSettings).first()
    if not settings:
        settings = models.PricingSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/pricing", response_model=schemas.PricingSettingsResponse)
def update_pricing_settings(settings: schemas.PricingSettingsUpdate, db: Session = Depends(database.get_db), current_admin: models.Admin = Depends(deps.get_current_admin)):
    db_settings = db.query(models.PricingSettings).first()
    if not db_settings:
        db_settings = models.PricingSettings()
        db.add(db_settings)
        
    for key, value in settings.model_dump().items():
        setattr(db_settings, key, value)
    
    db.commit()
    db.refresh(db_settings)
    return db_settings

from fastapi import UploadFile, File
import uuid
from .. import storage

@router.post("/pricing/qr-code", response_model=schemas.PricingSettingsResponse)
def upload_qr_code(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_admin: models.Admin = Depends(deps.get_current_admin)
):
    db_settings = db.query(models.PricingSettings).first()
    if not db_settings:
        db_settings = models.PricingSettings()
        db.add(db_settings)
        
    unique_filename = f"qr_{uuid.uuid4()}_{file.filename}"
    file_path = storage.save_file(file, unique_filename)
    
    db_settings.qr_code_path = file_path
    db.commit()
    db.refresh(db_settings)
    return db_settings

@router.get("/cost", response_model=schemas.CostSettingsResponse)
def get_cost_settings(db: Session = Depends(database.get_db), current_admin: models.Admin = Depends(deps.get_current_admin)):
    settings = db.query(models.CostSettings).first()
    if not settings:
        settings = models.CostSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/cost", response_model=schemas.CostSettingsResponse)
def update_cost_settings(settings: schemas.CostSettingsUpdate, db: Session = Depends(database.get_db), current_admin: models.Admin = Depends(deps.get_current_admin)):
    db_settings = db.query(models.CostSettings).first()
    if not db_settings:
        db_settings = models.CostSettings()
        db.add(db_settings)
        
    for key, value in settings.model_dump().items():
        setattr(db_settings, key, value)
    
    db.commit()
    db.refresh(db_settings)
    return db_settings

# Order Management
@router.get("/orders", response_model=list[schemas.OrderResponse])
def get_all_orders(db: Session = Depends(database.get_db), current_admin: models.Admin = Depends(deps.get_current_admin)):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()

def generate_pickup_code(db: Session) -> str:
    while True:
        code = f"CP{random.randint(1000, 9999)}"
        if not db.query(models.Order).filter(models.Order.pickup_code == code).first():
            return code

def update_customer_stats(db: Session, student_id: int):
    # CustomerStats refresh this row every time one of the student's orders changes status
    stats = db.query(models.CustomerStat).filter(models.CustomerStat.student_id == student_id).first()
    if not stats:
        stats = models.CustomerStat(student_id=student_id)
        db.add(stats)
        
    completed_orders = db.query(models.Order).filter(
        models.Order.student_id == student_id,
        models.Order.status == "COMPLETED"
    ).all()
    
    stats.total_orders = len(completed_orders)
    stats.total_pages = sum(o.pages * o.copies for o in completed_orders)
    stats.total_revenue = sum(o.grand_total for o in completed_orders)
    stats.lifetime_value = stats.total_revenue
    
    last_order = db.query(models.Order).filter(models.Order.student_id == student_id).order_by(models.Order.created_at.desc()).first()
    if last_order:
        stats.last_order_at = last_order.created_at
        
    db.commit()

@router.put("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, status_update: schemas.OrderStatusUpdate, db: Session = Depends(database.get_db), current_admin: models.Admin = Depends(deps.get_current_admin)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    new_status = status_update.status
    
    # State transitions
    if order.status == "PAYMENT_VERIFICATION":
        if new_status == "PAYMENT_RECEIVED":
            order.payment_verified_at = datetime.now(timezone.utc)
        elif new_status != "PENDING_PAYMENT":
            raise HTTPException(status_code=400, detail="Invalid status transition from PAYMENT_VERIFICATION")
            
    elif order.status == "PENDING_CASH":
        if new_status == "PAYMENT_RECEIVED":
            order.payment_verified_at = datetime.now(timezone.utc)
        elif new_status != "PENDING_PAYMENT":
            raise HTTPException(status_code=400, detail="Invalid status transition from PENDING_CASH")
            
    elif order.status == "PAYMENT_RECEIVED":
        if new_status == "PRINTING":
            pass # Just moving along the funnel
        else:
            raise HTTPException(status_code=400, detail="Invalid status transition from PAYMENT_RECEIVED")
            
    elif order.status == "PRINTING":
        if new_status == "READY_FOR_PICKUP":
            if not order.pickup_code:
                order.pickup_code = generate_pickup_code(db)
            order.ready_at = datetime.now(timezone.utc)
        else:
            raise HTTPException(status_code=400, detail="Invalid status transition from PRINTING")
            
    elif order.status == "READY_FOR_PICKUP":
        if new_status == "COMPLETED":
            order.completed_at = datetime.now(timezone.utc)
            # Log sales and profit
            log_sales_and_profit(db, order)
        else:
            raise HTTPException(status_code=400, detail="Invalid status transition from READY_FOR_PICKUP")
    else:
        raise HTTPException(status_code=400, detail=f"Admin cannot manually transition from {order.status}")
        
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    update_customer_stats(db, order.student_id)
    
    db.add(models.AuditLog(
        user_type="admin",
        user_identifier=current_admin.username,
        action="UPDATE_ORDER_STATUS",
        details=f"Order {order.order_number} status changed to {new_status}"
    ))
    db.commit()
    
    return order

def log_sales_and_profit(db: Session, order: models.Order):
    # Ensure we don't log twice
    if db.query(models.SalesLog).filter(models.SalesLog.order_id == order.id).first():
        return
        
    cost_settings = db.query(models.CostSettings).first()
    student = order.student
    
    import math
    if order.print_type == "multi_page":
        billable_pages = math.ceil(order.pages / 4.0)
    else:
        billable_pages = order.pages
        
    # Calculate costs
    paper_cost = cost_settings.paper_cost_per_sheet * (billable_pages * order.copies)
    printing_expense = cost_settings.printing_cost_per_page * (billable_pages * order.copies)
    ink_expense = cost_settings.ink_cost_per_page * (billable_pages * order.copies) if order.color == "color" else 0
    binding_expense = (cost_settings.spiral_binding_cost if order.binding == "spiral" else cost_settings.soft_binding_cost if order.binding == "soft" else 0) * order.copies
    
    total_expense = paper_cost + printing_expense + ink_expense + binding_expense
    revenue = order.printing_cost + order.binding_cost # Excluding GST for profit calculation
    profit = revenue - total_expense
    
    sales_log = models.SalesLog(
        order_id=order.id,
        student_name=student.name,
        mobile_number=student.mobile_number,
        pages=order.pages,
        copies=order.copies,
        printer_used=order.printer_used,
        paper_cost=paper_cost,
        selling_price=revenue,
        profit=profit,
        status=order.status
    )
    db.add(sales_log)
    
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    profit_log = models.ProfitLog(
        order_id=order.id,
        revenue=revenue,
        expense=total_expense,
        profit=profit,
        profit_margin_percent=profit_margin
    )
    db.add(profit_log)
    
    # Update inventory
    inventory_item = db.query(models.Inventory).first() # Assuming single paper type for now
    if inventory_item:
        inventory_item.current_stock -= (billable_pages * order.copies)
        
    db.commit()

@router.put("/orders/{order_id}/cancel", response_model=schemas.OrderResponse)
def cancel_order_admin(
    order_id: int, 
    db: Session = Depends(database.get_db),
    admin: models.Admin = Depends(deps.get_current_admin)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = "CANCELLED"
    
    # Audit Log
    db.add(models.AuditLog(
        user_type="admin",
        user_identifier=admin.username,
        action="CANCEL_ORDER",
        details=f"Order {order.order_number} cancelled by admin (was {old_status})"
    ))

    db.commit()
    db.refresh(order)
    return order

@router.delete("/orders/{order_id}")
def delete_order_admin(
    order_id: int, 
    db: Session = Depends(database.get_db),
    admin: models.Admin = Depends(deps.get_current_admin)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(order)
    
    # Audit Log
    db.add(models.AuditLog(
        user_type="admin",
        user_identifier=admin.username,
        action="DELETE_ORDER",
        details=f"Order {order.order_number} deleted entirely"
    ))

    db.commit()
    return {"detail": "Order deleted successfully"}

# Material Logs
@router.post("/materials", response_model=schemas.MaterialPurchaseResponse)
def create_material_purchase(
    purchase: schemas.MaterialPurchaseCreate,
    db: Session = Depends(database.get_db),
    admin: models.Admin = Depends(deps.get_current_admin)
):
    db_purchase = models.MaterialPurchaseLog(**purchase.model_dump())
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

@router.get("/materials", response_model=list[schemas.MaterialPurchaseResponse])
def get_material_purchases(
    db: Session = Depends(database.get_db),
    admin: models.Admin = Depends(deps.get_current_admin)
):
    return db.query(models.MaterialPurchaseLog).order_by(models.MaterialPurchaseLog.purchased_at.desc()).all()

# Analytics Control Chart
@router.get("/analytics/control-chart")
def get_control_chart_data(
    db: Session = Depends(database.get_db),
    admin: models.Admin = Depends(deps.get_current_admin)
):
    from sqlalchemy import func
    from collections import defaultdict
    
    # We will group by day (YYYY-MM-DD)
    # 1. Material Buying Logs Cost
    material_logs = db.query(
        func.date(models.MaterialPurchaseLog.purchased_at).label("date"),
        func.sum(models.MaterialPurchaseLog.total_cost).label("cost")
    ).group_by(func.date(models.MaterialPurchaseLog.purchased_at)).all()
    
    # 2. Revenue and Cost of Pages from ProfitLog
    # ProfitLog tracks expense and revenue
    profit_logs = db.query(
        func.date(models.ProfitLog.created_at).label("date"),
        func.sum(models.ProfitLog.revenue).label("revenue"),
        func.sum(models.ProfitLog.expense).label("expense"),
        models.Order.payment_method
    ).join(models.Order).group_by(func.date(models.ProfitLog.created_at), models.Order.payment_method).all()
    
    data_by_date = defaultdict(lambda: {"date": "", "material_cost": 0.0, "order_amount": 0.0, "cost_of_pages": 0.0, "cash_revenue": 0.0, "upi_revenue": 0.0})
    
    for log in material_logs:
        date_str = str(log.date)
        data_by_date[date_str]["date"] = date_str
        data_by_date[date_str]["material_cost"] += float(log.cost or 0)
        
    for log in profit_logs:
        date_str = str(log.date)
        data_by_date[date_str]["date"] = date_str
        data_by_date[date_str]["order_amount"] += float(log.revenue or 0)
        data_by_date[date_str]["cost_of_pages"] += float(log.expense or 0)
        
        if getattr(log, "payment_method", "upi") == "cash":
            data_by_date[date_str]["cash_revenue"] += float(log.revenue or 0)
        else:
            data_by_date[date_str]["upi_revenue"] += float(log.revenue or 0)
        
    # Sort by date
    sorted_data = sorted(data_by_date.values(), key=lambda x: x["date"])
    
    return sorted_data


import csv
import io
from ..storage import _upload_to_drive
import os

@router.post("/export-to-drive")
def export_data_to_drive(db: Session = Depends(database.get_db), admin: models.Admin = Depends(deps.get_current_admin)):
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        raise HTTPException(status_code=500, detail="Google Drive Folder ID not configured")
        
    # Generate CSV of Orders
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Order ID", "Date", "Student", "Mobile", "Pages", "Copies", "Print Type", "Color", "Payment Method", "Revenue", "Status"])
    
    for o in orders:
        writer.writerow([
            o.order_number, 
            o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else "", 
            o.student_name, 
            o.student.mobile_number if o.student else "", 
            o.pages, 
            o.copies, 
            o.print_type, 
            o.color, 
            o.payment_method, 
            o.grand_total, 
            o.status
        ])
    
    csv_content = output.getvalue()
    
    try:
        from googleapiclient.http import MediaIoBaseUpload
        media = MediaIoBaseUpload(io.BytesIO(csv_content.encode('utf-8')), mimetype='text/csv', resumable=True)
        drive_file = _upload_to_drive(media, f"campus_copies_export_{datetime.now().strftime('%Y%m%d%H%M')}.csv", folder_id)
        
        return {"detail": "Export successful", "drive_link": drive_file.get("webViewLink")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

