from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

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

class CustomerAttributes(ResourceAttributes):
    name: str
    email: str

class CustomerData(ResourceData):
    type: str = "customers"
    attributes: CustomerAttributes

class CustomerCreateRequest(BaseModel):
    data: CustomerData

class CustomerResponseAttributes(CustomerAttributes):
    created_at: datetime = Field(default_factory=datetime.now)

class CustomerResponseData(CustomerData):
    attributes: CustomerResponseAttributes

class CustomerSingleResponse(BaseModel):
    data: CustomerResponseData

# --- 2. FastAPI Application Setup ---

app = FastAPI(
    title="TCP Billing Microservice",
    version="1.0.0",
    description="Implements the Level 7 Specification for subscriptions, usage-based metering, and invoicing."
)

# --- 3. Mock Database (In-memory for scaffolding) ---
# This will be replaced by SQLAlchemy/PostgreSQL in the next phase
MOCK_DB = {}

# --- 4. API Endpoints (Phase 2.6 Implementation) ---

@app.post(
    "/api/v1/customers",
    response_model=CustomerSingleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a Customer (Phase 2.6)"
)
async def create_customer(request: CustomerCreateRequest):
    """
    Creates a new customer account based on the Phase 2.6 API Specification.
    """
    customer_id = uuid4()
    
    # Extract attributes from the JSON:API compliant request
    attributes = request.data.attributes
    
    # Create the mock database record
    new_customer = {
        "id": customer_id,
        "name": attributes.name,
        "email": attributes.email,
        "created_at": datetime.now()
    }
    MOCK_DB[customer_id] = new_customer
    
    # Construct the JSON:API compliant response
    response_attributes = CustomerResponseAttributes(
        name=new_customer["name"],
        email=new_customer["email"],
        created_at=new_customer["created_at"]
    )
    
    response_data = CustomerResponseData(
        id=customer_id,
        attributes=response_attributes
    )
    
    return CustomerSingleResponse(data=response_data)

# --- 5. Health Check ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "billing-microservice"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
