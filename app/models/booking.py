from sqlalchemy import Column, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Booking(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "booking"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("property.id"), nullable=False)
    price = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="Pending")

    user = relationship("User", back_populates="bookings")
    property = relationship("Property", back_populates="bookings")

    def __repr__(self):
        return f"<Booking(id={self.id}, property_id={self.property_id}, status={self.status})>"
