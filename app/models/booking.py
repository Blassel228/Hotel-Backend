from sqlalchemy import Column, String, DateTime, ForeignKey, Float, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Booking(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "booking"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    guest_id = Column(UUID(as_uuid=True), ForeignKey("guest.id"), nullable=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id"), nullable=False)
    price = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="Pending")
    special_requests = Column(String)

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    guest = relationship("Guest", back_populates="bookings", uselist=False)

    __table_args__ = (CheckConstraint("user_id IS NOT NULL OR guest_id IS NOT NULL", name="chk_booking_user_or_guest"),)
