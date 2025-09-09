import base64

from fastapi import UploadFile

from app.schemas.Image import ImageUpdate, ImageCreate
from app.utils.unitofwork import UnitOfWork


class ImageService:
    async def create(self, unit_of_work: UnitOfWork, user_id: int, file: UploadFile):
        image_data = await file.read()
        image_data = base64.b64encode(image_data).decode('utf-8')

        image = ImageCreate(file_name=file.filename, image_data=image_data, user_id=user_id)
        async with unit_of_work:
            return await unit_of_work.image.create(image)

    async def update(self, unit_of_work: UnitOfWork, user_id: int, file: UploadFile):
        image_data = await file.read()
        image_data = base64.b64encode(image_data).decode('utf-8')
        image = ImageUpdate(file_name=file.filename, image_data=image_data)
        async with unit_of_work:
            return await unit_of_work.image.update(image, id=user_id)
