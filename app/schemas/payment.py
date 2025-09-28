from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.guest import GuestCreateIn


class CreateCheckoutSessionRequest(BaseModel):
    room_id: str
    price: float = Field(..., gt=0)
    start_date: datetime
    end_date: datetime
    currency: str = Field(default="usd", pattern="^[a-zA-Z]{3}$")
    special_requests: Optional[str] = None
    guest_data: Optional[GuestCreateIn] = None


class CreateRefundRequest(BaseModel):
    booking_id: str
    refund_reason: str
