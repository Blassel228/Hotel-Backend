from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateCheckoutSessionRequest(BaseModel):
    room_id: str
    price: float = Field(..., gt=0)
    start_date: datetime
    end_date: datetime
    currency: str = Field(default="usd", pattern="^[a-zA-Z]{3}$")
    special_requests: Optional[str] = None


class CreateRefundRequestByUser(BaseModel):
    booking_id: str
    refund_reason: str


class CreateRefundRequestByAdmin(BaseModel):
    booking_id: str
    refund_reason: str
    amount: float = Field(gt=0, description="Refund amount in major currency units (e.g., USD)")
