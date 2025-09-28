from pydantic import BaseModel


class ImageCreate(BaseModel):
    file_name: str
    image_data: bytes


class ImageCreateIn(BaseModel):
    file_name: str


class ImageUpdate(BaseModel):
    file_name: str
    image_data: bytes


class ImageUpdateIn(BaseModel):
    file_name: str
