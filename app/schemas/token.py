from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TokenData(BaseModel):
    email: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    expires_in: int

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class RefreshTokenCreate(BaseModel):
    token: str
    user_id: UUID
    expires_at: datetime
    revoked: bool
    used: bool