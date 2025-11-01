from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel
from ..enums.user_sex import UserSex


class User(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "user"

    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    phone_number = Column(String, nullable=True, unique=True)
    country = Column(String, nullable=True)
    sex = Column(Integer, SQLEnum(UserSex, name="user_sex"), default=UserSex.NOT_KNOWN.value, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    birthdate = Column(DateTime, nullable=True)
    image_id = Column(UUID, ForeignKey("image.id", ondelete="CASCADE"), nullable=True)

    image = relationship("Image", back_populates="user", uselist=False, cascade="delete")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", cascade="all, delete-orphan")
    refunds = relationship("Refund", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
