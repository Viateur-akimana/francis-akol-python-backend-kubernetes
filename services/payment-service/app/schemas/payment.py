"""Pydantic schemas for Payment Service."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.models.payment import PaymentMethod, PaymentStatus
from pydantic import BaseModel, ConfigDict, Field


# Payment Schemas
class PaymentIntentCreate(BaseModel):
    """Schema for creating a payment intent."""

    course_id: int = Field(..., gt=0)
    payment_method: PaymentMethod
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    idempotency_key: Optional[str] = Field(
        None,
        max_length=255,
        description="Unique key to prevent duplicate payments from retries",
    )


class PaymentConfirm(BaseModel):
    """Schema for confirming a payment."""

    payment_intent_id: str = Field(..., min_length=1)


class PaymentRefund(BaseModel):
    """Schema for refunding a payment."""

    reason: Optional[str] = Field(None, max_length=500)


class PaymentResponse(BaseModel):
    """Schema for payment response."""

    id: int
    user_id: int
    course_id: int
    enrollment_id: Optional[int]
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    transaction_id: Optional[str]
    payment_intent_id: Optional[str]
    idempotency_key: Optional[str]
    failure_reason: Optional[str]
    refund_reason: Optional[str]
    refunded_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentIntentResponse(BaseModel):
    """Schema for payment intent response."""

    payment_id: int
    payment_intent_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    client_secret: Optional[str] = None


class PaginatedPaymentResponse(BaseModel):
    """Schema for paginated payment list response."""

    items: list[PaymentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseModel):
    """Schema for generic message response."""

    message: str


class PaymentStatsResponse(BaseModel):
    """Schema for payment statistics."""

    total_payments: int
    total_amount: Decimal
    completed_payments: int
    completed_amount: Decimal
    pending_payments: int
    failed_payments: int
    refunded_payments: int
    refunded_amount: Decimal
