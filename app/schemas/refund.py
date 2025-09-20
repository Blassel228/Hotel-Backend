from uuid import UUID

from pydantic import BaseModel


class CreateRefund(BaseModel):
    booking_id: UUID
    refund_amount: float
    stripe_refund_id: str
    refund_reason: str
