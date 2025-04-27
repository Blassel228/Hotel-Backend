from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone_number: str
    name: str
    surname: str
    money_balance: Optional[float] = 0


class UserGet(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    phone_number: str
    name: str
    surname: str
    money_balance: float
