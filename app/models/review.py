from sqlalchemy import Column, Float, ForeignKey, Boolean, String, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class Review(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "review"

    stars = Column(Float, nullable=False)
    staff_rate = Column(Integer, nullable=False)
    cleanliness_rate = Column(Integer, nullable=False)
    title = Column(String, nullable=True)
    recommended_for_friends = Column(Boolean, nullable=False)
    stay_again = Column(Boolean, nullable=False)
    experience_comment = Column(String, nullable=True)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("booking.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("room.id", ondelete="CASCADE"), nullable=False)

    booking = relationship("Booking", back_populates="review")
    user = relationship("User", back_populates="reviews")
    room = relationship("Room", back_populates="reviews")

    __table_args__ = (
        CheckConstraint("stars >= 1 AND stars <= 10", name="check_stars_range"),
        CheckConstraint("staff_rate >= 1 AND staff_rate <= 4", name="check_staff_rate_range"),
        CheckConstraint("cleanliness_rate >= 1 AND cleanliness_rate <= 4", name="check_cleanliness_rate_range"),
        UniqueConstraint("booking_id", name="uq_review_booking"),
    )