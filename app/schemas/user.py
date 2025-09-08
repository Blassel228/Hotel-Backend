from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    country: str
    email: EmailStr
    phone_number: str
    name: str
    surname: str
    money_balance: Optional[float] = 0


class UserGet(BaseModel):
    username: str
    country: str
    email: EmailStr
    phone_number: str
    name: str
    surname: str
    money_balance: float

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    sex: Optional[int] = None
    birthdate: Optional[datetime] = None
