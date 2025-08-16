from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class GuestCreateIn(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: PhoneNumber
    country: Optional[str] = None
    whether_send_confirmation: bool = True
    is_booking_for_me: bool = True


class GuestCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: PhoneNumber
    country: Optional[str] = None
    whether_send_confirmation: bool = True
    is_booking_for_me: bool = True
