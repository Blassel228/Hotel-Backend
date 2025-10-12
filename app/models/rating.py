from sqlalchemy import Column, Float, UUID, ForeignKey, Boolean, String, Integer, CheckConstraint
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Rating(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "rating"

    stars = Column(
        Float,
        nullable=False,
    )
    staff_rate = Column(
        Integer,
        nullable=False,
    )
    cleanliness_rate = Column(
        Integer,
        nullable=False,
    )
    title = Column(String, nullable=True)
    recommended_for_friends = Column(Boolean, nullable=False)
    stay_again = Column(Boolean, nullable=False)
    experience_comment = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id"), nullable=False)

    room = relationship("Room", back_populates="ratings")

    __table_args__ = (
        CheckConstraint("staff_rate >= 1 AND staff_rate <= 4", name="check_staff_rate_range"),
        CheckConstraint("cleanliness_rate >= 1 AND cleanliness_rate <= 4", name="check_cleanliness_rate_range"),
    )
