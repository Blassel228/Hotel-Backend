from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, field_validator


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
    guest_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
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
