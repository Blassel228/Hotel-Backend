from sqlalchemy import ForeignKey, Column, String, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, CreatedAtModel, UUIDModel


class Image(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "image"

    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    file_name = Column(String, nullable=False)
    image_data = Column(LargeBinary, nullable=True)

    user = relationship("User", back_populates="image", uselist=False)

