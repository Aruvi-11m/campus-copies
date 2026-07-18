from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .. import models, schemas, database
import os
from datetime import datetime, timezone
import random

router = APIRouter(prefix="/agent", tags=["agent"])

AGENT_KEY = os.environ.get("AGENT_API_KEY", "default-agent-key-change-me")

def verify_agent_key(x_agent_key: str = Header(...)):
    if x_agent_key != AGENT_KEY:
        raise HTTPException(status_code=403, detail="Invalid Agent Key")
    return True

@router.get("/orders/pending", response_model=list[schemas.OrderResponse])
def get_pending_orders(db: Session = Depends(database.get_db), authorized: bool = Depends(verify_agent_key)):
    return db.query(models.Order).filter(models.Order.status == "PAYMENT_RECEIVED").all()

@router.put("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status_by_agent(
    order_id: int, 
    status_update: schemas.OrderStatusUpdate, 
    db: Session = Depends(database.get_db), 
    authorized: bool = Depends(verify_agent_key)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    new_status = status_update.status
    
    if new_status == "PRINTING":
        order.printed_at = datetime.now(timezone.utc)
    elif new_status == "READY_FOR_PICKUP":
        if not order.pickup_code:
            # Generate pickup code
            while True:
                code = f"CP{random.randint(1000, 9999)}"
                if not db.query(models.Order).filter(models.Order.pickup_code == code).first():
                    order.pickup_code = code
                    break
        order.ready_at = datetime.now(timezone.utc)
        
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    return order

@router.post("/logs")
def create_print_log(
    order_id: int,
    printer_used: str,
    options_used: str,
    status: str,
    error_message: str = None,
    db: Session = Depends(database.get_db),
    authorized: bool = Depends(verify_agent_key)
):
    log = models.PrintLog(
        order_id=order_id,
        printer_used=printer_used,
        options_used=options_used,
        status=status,
        error_message=error_message
    )
    if status in ["success", "failed"]:
        log.finished_at = datetime.now(timezone.utc)
        
    db.add(log)
    db.commit()
    return {"status": "ok"}
