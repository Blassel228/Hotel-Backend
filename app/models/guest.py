from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Guest(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "guest"

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    country = Column(String)
    whether_send_confirmation = Column(Boolean, nullable=False)
    is_booking_for_me = Column(Boolean, nullable=False)

    bookings = relationship("Booking", back_populates="guest")
