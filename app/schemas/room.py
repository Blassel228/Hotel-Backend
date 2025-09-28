from typing import Optional

from pydantic import BaseModel, Field

from app.enums.room_areas import RoomAreas
from app.enums.room_types import RoomType


class RoomBase(BaseModel):
    type: str = Field(..., description="Type of room (e.g., Suite, Deluxe, Standard)")
    price: int = Field(..., description="Price per night")
    beds: int = Field(..., description="Number of beds")
    bedrooms: int = Field(..., description="Number of bedrooms")
    bathes: int = Field(..., description="Number of bathrooms")
    floor: int = Field(..., description="Floor number")
    area: str = Field(..., description="Area or view (e.g., Ocean View)")
    has_sauna: bool = Field(..., description="Whether the room has a sauna")
    has_jacuzzi: bool = Field(..., description="Whether the room has a jacuzzi")
    description: str = Field(..., description="Room description")
    total_space: float = Field(..., description="Room size")
    capacity: int = Field(..., description="Number of people for the room")
    image: bytes = Field(None, description="Binary image data (LargeBinary)")


class RoomFilters(BaseModel):
    type: Optional[str] = None
    capacity: Optional[int] = None
    area: Optional[RoomAreas] = None
    bedrooms: Optional[int] = None
    bathes: Optional[int] = None


class RoomFilterParams:
    def __init__(
        self,
        lowest_price: float | None = None,
        greatest_price: float | None = None,
        type: RoomType | None = None,
        capacity: int | None = None,
        area: RoomAreas | None = None,
        bedrooms: int | None = None,
        bathes: int | None = None,
    ):
        self.lowest_price = lowest_price
        self.greatest_price = greatest_price
        self.type = type
        self.capacity = capacity
        self.area = area
        self.bedrooms = bedrooms
        self.bathes = bathes
