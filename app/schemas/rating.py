from uuid import UUID

from pydantic import BaseModel


class RatingAverageGet(BaseModel):
    room_id: UUID
    stars: float


class RatingCreate(BaseModel):
    user_id: UUID
    room_id: UUID
    stars: float


class RatingCreateIn(BaseModel):
    room_id: UUID
    stars: float
