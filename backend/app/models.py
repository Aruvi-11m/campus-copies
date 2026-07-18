from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    department = Column(String)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    orders = relationship("Order", back_populates="student")
    stats = relationship("CustomerStat", back_populates="student", uselist=False)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

class PricingSettings(Base):
    __tablename__ = "pricing_settings"

    id = Column(Integer, primary_key=True, index=True)
    single_side_price = Column(Float, default=0.0)
    double_side_price = Column(Float, default=0.0)
    multi_page_price = Column(Float, default=0.0)
    color_price = Column(Float, default=0.0)
    spiral_binding_price = Column(Float, default=0.0)
    soft_binding_price = Column(Float, default=0.0)
    gst_percent = Column(Float, default=18.0)
    upi_id = Column(String, nullable=True)
    qr_code_path = Column(String, nullable=True)
    service_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class CostSettings(Base):
    __tablename__ = "cost_settings"

    id = Column(Integer, primary_key=True, index=True)
    paper_cost_per_sheet = Column(Float, default=0.0)
    printing_cost_per_page = Column(Float, default=0.0)
    ink_cost_per_page = Column(Float, default=0.0)
    spiral_binding_cost = Column(Float, default=0.0)
    soft_binding_cost = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"))
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    pages = Column(Integer, nullable=False)
    copies = Column(Integer, default=1)
    print_type = Column(String, nullable=False) # single_side, double_side, multi_page
    color = Column(String, nullable=False) # black_white, color
    binding = Column(String, nullable=False) # none, spiral, soft
    notes = Column(String, nullable=True)
    
    printing_cost = Column(Float, default=0.0)
    binding_cost = Column(Float, default=0.0)
    gst_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    
    status = Column(String, default="PENDING_PAYMENT") 
    payment_transaction_id = Column(String, nullable=True)
    payment_screenshot_path = Column(String, nullable=True)
    pickup_code = Column(String, unique=True, index=True, nullable=True)
    printer_used = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    payment_submitted_at = Column(DateTime(timezone=True), nullable=True)
    payment_verified_at = Column(DateTime(timezone=True), nullable=True)
    printed_at = Column(DateTime(timezone=True), nullable=True)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    feedback_rating = Column(Integer, nullable=True)
    feedback_text = Column(String, nullable=True)

    student = relationship("Student", back_populates="orders")
    sales_logs = relationship("SalesLog", back_populates="order")
    profit_logs = relationship("ProfitLog", back_populates="order")
    print_logs = relationship("PrintLog", back_populates="order")

    @property
    def student_name(self):
        return self.student.name if self.student else None

    @property
    def student_department(self):
        return self.student.department if self.student else None

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    paper_type = Column(String, nullable=False)
    current_stock = Column(Integer, default=0)
    cost_per_sheet = Column(Float, default=0.0)
    reorder_level = Column(Integer, default=0)
    supplier = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class SalesLog(Base):
    __tablename__ = "sales_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    student_name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)
    pages = Column(Integer, nullable=False)
    copies = Column(Integer, nullable=False)
    printer_used = Column(String, nullable=True)
    paper_cost = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    order = relationship("Order", back_populates="sales_logs")

class CustomerStat(Base):
    __tablename__ = "customer_stats"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)
    total_orders = Column(Integer, default=0)
    total_pages = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    lifetime_value = Column(Float, default=0.0)
    last_order_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    student = relationship("Student", back_populates="stats")

class ProfitLog(Base):
    __tablename__ = "profit_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    revenue = Column(Float, default=0.0)
    expense = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    profit_margin_percent = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    order = relationship("Order", back_populates="profit_logs")

class PrintLog(Base):
    __tablename__ = "print_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    printer_used = Column(String, nullable=True)
    options_used = Column(String, nullable=True)
    status = Column(String, nullable=False) # success, failed, manual_pending
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), default=utcnow)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    order = relationship("Order", back_populates="print_logs")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow)
    user_type = Column(String, nullable=False) # student, admin, system
    user_identifier = Column(String, nullable=False) # e.g. mobile number or admin username
    action = Column(String, nullable=False)
    details = Column(String, nullable=True)

class AnalyticsCache(Base):
    __tablename__ = "analytics_cache"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True, nullable=False)
    period_key = Column(String, index=True, nullable=False) # e.g. 2026-07-17
    value = Column(Float, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
