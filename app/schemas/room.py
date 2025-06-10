from pydantic import BaseModel, Field


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
