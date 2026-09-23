
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    application_id: int | None = None
    member_id: str | None = None
    membership_category: str | None = None
    amount: Decimal
    currency: str = "INR"
    payment_method: str | None = None
    payment_gateway: str | None = None
    transaction_id: str | None = None
    payment_status: str = "Pending"
    paid_at: datetime | None = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    application_id: int | None = None
    member_id: str | None = None
    membership_category: str | None = None
    amount: Decimal
    currency: str
    payment_method: str | None = None
    payment_gateway: str | None = None
    transaction_id: str | None = None
    payment_status: str
    paid_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
