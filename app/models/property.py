from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Property(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "property"

    image = Column(
        LargeBinary(length=2**24),
        nullable=False,
    )
    type = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    area = Column(String, nullable=False)
    floor = Column(Integer, nullable=False)
    parking_spots = Column(Integer, nullable=False)
    total_space = Column(String, nullable=False)
    contract_status = Column(String, nullable=False)
    payment_process = Column(String, nullable=False)
    safety_feature = Column(String, nullable=False)

    bookings = relationship("Booking", back_populates="property")

    def __repr__(self):
        return f"<Property(id={self.id}, type={self.type}, address={self.address})>"
