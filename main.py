from fastapi import FastAPI, HTTPException, status
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sql_update

from database import get_db
from models import Customer, Subscription, UsageRecord, Plan

# --- 1. JSON:API Compliant Pydantic Models ---

# Base JSON:API Structure for Request/Response
class ResourceAttributes(BaseModel):
    """Base class for resource attributes."""
    pass

class ResourceData(BaseModel):
    """Base class for JSON:API data object."""
    id: Optional[UUID] = Field(default_factory=uuid4)
    type: str
    attributes: ResourceAttributes

class SingleResourceResponse(BaseModel):
    """Base class for a single resource response."""
    data: ResourceData

# --- Customer Models ---

class CustomerAttributes(ResourceAttributes):
    name: str
    email: str

class CustomerData(ResourceData):
    type: str = "customers"
    attributes: CustomerAttributes

class CustomerCreateRequest(BaseModel):
    data: CustomerData

class CustomerResponseAttributes(CustomerAttributes):
    created_at: datetime

class CustomerResponseData(CustomerData):
    attributes: CustomerResponseAttributes

class CustomerSingleResponse(BaseModel):
    data: CustomerResponseData

# --- Subscription Models ---

class SubscriptionCreateAttributes(ResourceAttributes):
    customer_id: UUID
    plan_id: UUID

class SubscriptionCreateData(ResourceData):
    type: str = "subscriptions"
    attributes: SubscriptionCreateAttributes

class SubscriptionCreateRequest(BaseModel):
    data: SubscriptionCreateData

class SubscriptionUpdateAttributes(ResourceAttributes):
    status: Optional[str] = None # e.g., 'canceled'

class SubscriptionUpdateData(ResourceData):
    type: str = "subscriptions"
    attributes: SubscriptionUpdateAttributes

class SubscriptionUpdateRequest(BaseModel):
    data: SubscriptionUpdateData

class SubscriptionResponseAttributes(SubscriptionCreateAttributes):
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime

class SubscriptionResponseData(ResourceData):
    type: str = "subscriptions"
    attributes: SubscriptionResponseAttributes

class SubscriptionSingleResponse(BaseModel):
    data: SubscriptionResponseData

# --- Usage Record Models ---

class UsageRecordAttributes(ResourceAttributes):
    subscription_id: UUID
    metric_name: str
    quantity: int

class UsageRecordData(ResourceData):
    type: str = "usage-records"
    attributes: UsageRecordAttributes

class UsageRecordCreateRequest(BaseModel):
    data: UsageRecordData

# --- 2. FastAPI Application Setup ---

app = FastAPI(
    title="TCP Billing Microservice",
    version="1.0.0",
    description="Implements the Level 7 Specification for subscriptions, usage-based metering, and invoicing."
)

# --- 3. API Endpoints (Phase 2.6 Implementation) ---

# Helper function to convert ORM model to Pydantic response model
def customer_to_response(customer: Customer) -> CustomerSingleResponse:
    attrs = CustomerResponseAttributes(
        name=customer.name,
        email=customer.email,
        created_at=customer.created_at
    )
    data = CustomerResponseData(
        id=customer.id,
        attributes=attrs
    )
    return CustomerSingleResponse(data=data)

def subscription_to_response(subscription: Subscription) -> SubscriptionSingleResponse:
    attrs = SubscriptionResponseAttributes(
        customer_id=subscription.customer_id,
        plan_id=subscription.plan_id,
        status=subscription.status,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        created_at=subscription.created_at
    )
    data = SubscriptionResponseData(
        id=subscription.id,
        attributes=attrs
    )
    return SubscriptionSingleResponse(data=data)


# --- Customer Management ---

@app.post(
    "/api/v1/customers",
    response_model=CustomerSingleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Customer (Phase 2.6)"
)
async def create_customer(
    request: CustomerCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new customer account based on the Phase 2.6 API Specification.
    """
    attributes = request.data.attributes
    
    # Check for existing customer by email
    result = await db.execute(select(Customer).where(Customer.email == attributes.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer with this email already exists."
        )

    new_customer = Customer(
        name=attributes.name,
        email=attributes.email
    )
    
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    
    return customer_to_response(new_customer)

# --- Subscription Management ---

@app.post(
    "/api/v1/subscriptions",
    response_model=SubscriptionSingleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Subscription (Phase 2.6)"
)
async def create_subscription(
    request: SubscriptionCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a new subscription for a customer.
    """
    attributes = request.data.attributes
    
    # 1. Validate Customer Exists
    customer_result = await db.execute(select(Customer).where(Customer.id == attributes.customer_id))
    if not customer_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {attributes.customer_id} not found."
        )

    # 2. Validate Plan Exists (Mocking for now, as Plan table is empty)
    # In a real system, we would check the Plan table. For MVP, we assume the plan_id is valid.
    # plan_result = await db.execute(select(Plan).where(Plan.id == attributes.plan_id))
    # if not plan_result.scalars().first():
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"Plan with ID {attributes.plan_id} not found."
    #     )

    new_subscription = Subscription(
        customer_id=attributes.customer_id,
        plan_id=attributes.plan_id,
        status="active", # Default status for new subscription
        start_date=datetime.now()
    )
    
    db.add(new_subscription)
    await db.commit()
    await db.refresh(new_subscription)
    
    # TODO: Phase 2.7 - Publish subscription.created event here
    
    return subscription_to_response(new_subscription)

@app.patch(
    "/api/v1/subscriptions/{subscriptionId}",
    response_model=SubscriptionSingleResponse,
    summary="Update/Cancel a Subscription (Phase 2.6)"
)
async def update_subscription(
    subscriptionId: UUID,
    request: SubscriptionUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates the status of an active subscription (e.g., to 'canceled').
    """
    attributes = request.data.attributes
    
    # 1. Find Subscription
    subscription_result = await db.execute(select(Subscription).where(Subscription.id == subscriptionId))
    subscription = subscription_result.scalars().first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscriptionId} not found."
        )

    # 2. Apply Updates
    update_data = {}
    if attributes.status == "canceled":
        update_data["status"] = "canceled"
        update_data["end_date"] = datetime.now()
    elif attributes.status:
        update_data["status"] = attributes.status
    
    if not update_data:
        return subscription_to_response(subscription) # No change

    # Perform the update
    await db.execute(
        sql_update(Subscription)
        .where(Subscription.id == subscriptionId)
        .values(**update_data)
    )
    await db.commit()
    
    # Re-fetch the updated subscription
    updated_subscription_result = await db.execute(select(Subscription).where(Subscription.id == subscriptionId))
    updated_subscription = updated_subscription_result.scalars().first()
    
    # TODO: Phase 2.7 - Publish subscription.updated event here
    
    return subscription_to_response(updated_subscription)

# --- Usage Reporting ---

@app.post(
    "/api/v1/usage-records",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Report Usage (Phase 2.6)"
)
async def report_usage(
    request: UsageRecordCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reports a usage event for a subscription. Returns 202 Accepted as processing is asynchronous.
    """
    attributes = request.data.attributes
    
    # 1. Validate Subscription Exists
    subscription_result = await db.execute(select(Subscription).where(Subscription.id == attributes.subscription_id))
    if not subscription_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {attributes.subscription_id} not found."
        )

    # 2. Create Usage Record
    new_usage_record = UsageRecord(
        subscription_id=attributes.subscription_id,
        metric_name=attributes.metric_name,
        quantity=attributes.quantity,
        timestamp=datetime.now()
    )
    
    db.add(new_usage_record)
    await db.commit()
    
    # TODO: This is where the complex usage aggregation and billing logic would go.
    # For MVP, we just store the record.
    
    return {"meta": {"status": "Usage record accepted for processing."}}


# --- Health Check ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "billing-microservice"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
