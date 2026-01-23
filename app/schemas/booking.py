from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.enums.booking_status import BookingStatus


class CreateBookingIn(BaseModel):
    room_id: UUID
    price: Decimal
    special_requests: str
    start_date: datetime
    end_date: datetime

    @field_validator("start_date", "end_date", mode="before")
    def dt_validate(cls, value) -> datetime:
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.replace(tzinfo=None)


class CreateBooking(BaseModel):
    user_id: Optional[UUID] = None
    intent_id: str
    status: str = BookingStatus.CONFIRMED.value
    room_id: UUID
    price: Decimal
    special_requests: Optional[str] = None
    start_date: datetime
    end_date: datetime

    @field_validator("start_date", "end_date", mode="before")
    def dt_validate(cls, value) -> datetime:
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.replace(tzinfo=None)


class UpdateBooking(BaseModel):
    user_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    price: Optional[float] = None
    status: Optional[str] = BookingStatus.CONFIRMED.value
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
