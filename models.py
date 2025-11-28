from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from uuid import uuid4

# Helper for UUID primary keys
def uuid_pk():
    return Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

class Customer(Base):
    __tablename__ = "customer"
    
    id = uuid_pk()
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    subscriptions = relationship("Subscription", back_populates="customer")
    payment_methods = relationship("PaymentMethod", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")

class Product(Base):
    __tablename__ = "product"
    
    id = uuid_pk()
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    plans = relationship("Plan", back_populates="product")

class Plan(Base):
    __tablename__ = "plan"
    
    id = uuid_pk()
    product_id = Column(UUID(as_uuid=True), ForeignKey("product.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    product = relationship("Product", back_populates="plans")
    prices = relationship("Price", back_populates="plan")
    subscriptions = relationship("Subscription", back_populates="plan")

class Price(Base):
    __tablename__ = "price"
    
    id = uuid_pk()
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plan.id"), nullable=False)
    currency = Column(String, nullable=False)
    unit_amount = Column(Integer, nullable=False)
    recurring_interval = Column(String, nullable=True) # e.g., 'month', 'year'
    created_at = Column(DateTime, default=func.now())
    
    plan = relationship("Plan", back_populates="prices")

class Subscription(Base):
    __tablename__ = "subscription"
    
    id = uuid_pk()
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plan.id"), nullable=False)
    status = Column(String, nullable=False) # e.g., 'active', 'canceled', 'past_due'
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    customer = relationship("Customer", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    usage_records = relationship("UsageRecord", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription")

class UsageRecord(Base):
    __tablename__ = "usage_record"
    
    id = uuid_pk()
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscription.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    subscription = relationship("Subscription", back_populates="usage_records")
    line_item = relationship("LineItem", back_populates="usage_record", uselist=False)

class Invoice(Base):
    __tablename__ = "invoice"
    
    id = uuid_pk()
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscription.id"), nullable=True)
    status = Column(String, nullable=False) # e.g., 'draft', 'open', 'paid', 'void'
    currency = Column(String, nullable=False)
    total_amount = Column(Integer, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    customer = relationship("Customer", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
    line_items = relationship("LineItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")

class LineItem(Base):
    __tablename__ = "line_item"
    
    id = uuid_pk()
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=False)
    usage_record_id = Column(UUID(as_uuid=True), ForeignKey("usage_record.id"), nullable=True)
    description = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    invoice = relationship("Invoice", back_populates="line_items")
    usage_record = relationship("UsageRecord", back_populates="line_item")

class Payment(Base):
    __tablename__ = "payment"
    
    id = uuid_pk()
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoice.id"), nullable=False)
    status = Column(String, nullable=False) # e.g., 'succeeded', 'failed'
    currency = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    stripe_payment_intent_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    invoice = relationship("Invoice", back_populates="payments")

class PaymentMethod(Base):
    __tablename__ = "payment_method"
    
    id = uuid_pk()
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer.id"), nullable=False)
    type = Column(String, nullable=False) # e.g., 'card', 'bank_transfer'
    stripe_payment_method_id = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    customer = relationship("Customer", back_populates="payment_methods")
