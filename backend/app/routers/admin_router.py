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
    
    # Calculate costs
    paper_cost = cost_settings.paper_cost_per_sheet * (order.pages * order.copies)
    printing_expense = cost_settings.printing_cost_per_page * (order.pages * order.copies)
    ink_expense = cost_settings.ink_cost_per_page * (order.pages * order.copies) if order.color == "color" else 0
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
        inventory_item.current_stock -= (order.pages * order.copies)
        
    db.commit()
