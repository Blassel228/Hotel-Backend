from datetime import datetime
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, field_validator


class CreateBookingIn(BaseModel):
    room_id: UUID
    start_date: datetime
    end_date: datetime
    price: Decimal
    special_requests: str

    @field_validator("start_date", "end_date", mode='before')
    def dt_validate(cls, value) -> datetime:
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.replace(tzinfo=None)


class CreateBooking(BaseModel):
    user_id: UUID
    room_id: UUID
    start_date: datetime
    price: Decimal
    special_requests: str
    end_date: datetime

    @field_validator("start_date", "end_date", mode='before')
    def dt_validate(cls, value) -> datetime:
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.replace(tzinfo=None)