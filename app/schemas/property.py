from pydantic import BaseModel, Field


class PropertyBase(BaseModel):
    type: str = Field(..., description="Type of property (e.g., Hotel, Villa)")
    price: int = Field(..., description="Price of the property")
    address: str = Field(..., description="Address of the property")
    bedrooms: int = Field(..., description="Number of bedrooms")
    bathrooms: int = Field(..., description="Number of bathrooms")
    area: str = Field(..., description="Area or neighborhood")
    floor: int = Field(..., description="Floor number")
    parking_spots: int = Field(..., description="Number of parking spots")
    total_space: str = Field(..., description="Total space (e.g., 2000 sq ft)")
    contract_status: str = Field(..., description="Contract status")
    payment_process: str = Field(..., description="Payment process details")
    safety_feature: str = Field(..., description="Safety features")
    image: bytes = Field(None, description="Binary image data (LargeBinary)")
