from sqlalchemy import Column, LargeBinary, UUID, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, CreatedAtModel, UUIDModel


class RoomImage(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "room_image"

    image = Column(
        LargeBinary(length=2 ** 24),
        nullable=False,
    )

    room_id = Column(UUID, ForeignKey("room.id"), nullable=False)
    room = relationship("Room", back_populates="image")