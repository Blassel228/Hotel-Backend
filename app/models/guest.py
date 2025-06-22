from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, CreatedAtModel, UUIDModel

class Guest(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "guest"

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=False)
    phone = Column(String, nullable=False, unique=False)
    country = Column(String)
    whether_send_confirmation = Column(Boolean, nullable=False)
    is_booking_for_me = Column(Boolean, nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("booking.id"), unique=True)

    booking = relationship("Booking", back_populates="guest")
