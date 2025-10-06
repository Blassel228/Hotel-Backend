from sqlalchemy import Column, Float, UUID, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Rating(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "rating"

    stars = Column(Float, nullable=False,)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id"), nullable=False)

    room = relationship("Room", back_populates="ratings")
