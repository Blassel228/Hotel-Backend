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
