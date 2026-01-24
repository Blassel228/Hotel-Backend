from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmailIn(BaseModel):
    id: UUID
    start_date: datetime
    end_date: datetime
    price: float


class ChangeEmailRequest(BaseModel):
    new_email: str
    password: str
