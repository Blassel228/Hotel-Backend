from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


class User(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "user"

    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    money_balance = Column(Float, nullable=False, default=0.0)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    phone_number = Column(String, nullable=True, unique=True)

    bookings = relationship("Booking", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
