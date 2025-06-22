from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Booking(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "booking"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id"), nullable=False)
    price = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="Pending")
    special_requests = Column(String, nullable=True, default=None)

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    guest = relationship("Guest", back_populates="booking", uselist=False)


    def __repr__(self):
        return f"<Booking(id={self.id}, room_id={self.room_id}, status={self.status})>"
