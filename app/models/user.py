from sqlalchemy import Column, String, DECIMAL
from sqlalchemy.orm import relationship

from .base import Base, CreatedAtModel, UUIDModel


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

    bookings = relationship("Booking", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
