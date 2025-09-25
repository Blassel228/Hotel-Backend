from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, CreatedAtModel, UUIDModel

class RefreshToken(Base, CreatedAtModel, UUIDModel):
    __tablename__ = "refresh_token"

    token = Column(String(512), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)

    expires_at = Column(DateTime, nullable=False)

    revoked = Column(Boolean, default=False, nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<RefreshToken(user_id={self.user_id}, revoked={self.revoked})>"