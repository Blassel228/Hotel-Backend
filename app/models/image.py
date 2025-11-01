from sqlalchemy import Column, String, LargeBinary
from sqlalchemy.orm import relationship

from app.models.base import Base, CreatedAtModel, UUIDModel


class Image(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "image"

    file_name = Column(String, nullable=False)
    image_data = Column(LargeBinary, nullable=True)

    user = relationship("User", back_populates="image")
