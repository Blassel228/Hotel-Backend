# from sqlalchemy import Column, String
# from sqlalchemy.orm import relationship
#
# from app.models.base import Base, CreatedAtModel, UUIDModel
#
#
# class ImageUrl(Base, CreatedAtModel, UUIDModel):
#     __tablename__ = "image_url"
#
#     file_name = Column(String, nullable=False)
#     image_url = Column(String, nullable=False)
#
#     user = relationship("User", back_populates="image_url", uselist=False)
