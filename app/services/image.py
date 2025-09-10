import base64

from fastapi import UploadFile

from app.schemas.Image import ImageUpdate, ImageCreate
from app.utils.unitofwork import UnitOfWork


class ImageService:
    async def get_one(self, unit_of_work: UnitOfWork, image_id: int):
        async with unit_of_work:
            return await unit_of_work.image.get_one(id=image_id)

    async def create(self, unit_of_work: UnitOfWork, user_id: int, file: UploadFile):
        image_data = await file.read()
        image_data = base64.b64encode(image_data).decode('utf-8')

        image = ImageCreate(file_name=file.filename, image_data=image_data)
        async with unit_of_work:
            image = await unit_of_work.image.create(image)
            await unit_of_work.user.update({"image_id": image.id}, id=user_id)
            return image

    async def update(self, unit_of_work: UnitOfWork, user_id: int, file: UploadFile):
        async with unit_of_work:
            user = await unit_of_work.user.get_one(id=user_id)
        image_data = await file.read()
        image_data = base64.b64encode(image_data).decode('utf-8')
        image = ImageUpdate(file_name=file.filename, image_data=image_data)
        async with unit_of_work:
            await unit_of_work.image.update(image, id=user.image_id)
            return await unit_of_work.image.get_one(id=user.image_id)
