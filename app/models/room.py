from sqlalchemy import Column, String, Integer, Boolean, Float
from sqlalchemy.orm import relationship
from .base import Base, CreatedAtModel, UUIDModel


class Room(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "room"

    type = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    beds = Column(Integer, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathes = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)
    area = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    total_space = Column(Float, nullable=False)
    has_sauna = Column(Boolean, nullable=False)
    has_jacuzzi = Column(Boolean, nullable=False)

    image = relationship("RoomImage", back_populates="room")

    bookings = relationship("Booking", back_populates="room")

    def __repr__(self):
        return f"<Room(id={self.id}, type={self.type}, area={self.area})>"