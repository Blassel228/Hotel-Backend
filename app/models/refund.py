from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Refund(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "refund"

    booking_id = Column(UUID(as_uuid=True), ForeignKey("booking.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    stripe_refund_id = Column(String, nullable=False, unique=True)
    refund_amount = Column(Float, nullable=False)
    refund_reason = Column(String, nullable=False)

    booking = relationship("Booking", back_populates="refund")
    user = relationship("User", back_populates="refunds")
