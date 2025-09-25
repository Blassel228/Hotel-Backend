from sqlalchemy import Column, String, DECIMAL, DateTime, Integer, ForeignKey
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
    country = Column(String, nullable=False)
    money_balance = Column(DECIMAL, nullable=False)
    sex = Column(Integer, SQLEnum(UserSex, name="user_sex"), default=UserSex.NOT_KNOWN.value, nullable=False)
    birthdate = Column(DateTime, nullable=True)
    image_id = Column(UUID, ForeignKey("image.id"), nullable=True)

    image = relationship("Image", back_populates="user", uselist=False)
    bookings = relationship("Booking", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
