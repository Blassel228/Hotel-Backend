from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ReviewAverageGet(BaseModel):
    average_rating: float | None


class ReviewCreate(BaseModel):
    user_id: UUID
    room_id: UUID
    stars: float
    recommended_for_friends: bool
    stay_again: bool
    experience_comment: Optional[str] = None
    title: Optional[str] = None
    staff_rate: int
    cleanliness_rate: int


class ReviewCreateIn(BaseModel):
    room_id: UUID
    stars: float
    recommended_for_friends: bool
    stay_again: bool
    title: Optional[str] = None
    experience_comment: Optional[str] = None
    staff_rate: int
    cleanliness_rate: int
