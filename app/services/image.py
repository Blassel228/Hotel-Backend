import base64

from fastapi import UploadFile, status

from app.core.exc.base import ObjectNotFoundException
from app.schemas.Image import ImageUpdate, ImageCreate
from app.utils.unitofwork import UnitOfWork


class ImageService:
    async def get_one(self, unit_of_work: UnitOfWork, user_id: int):
        async with unit_of_work:
            user = await unit_of_work.user.get_one(id=user_id)
            if user.image_id is None:
                return None
            image = await unit_of_work.image.get_one(id=user.image_id)
        return image

    async def create(self, unit_of_work: UnitOfWork, user_id: int, file: UploadFile):
        if not file.content_type or not file.content_type.startswith("image/"):
            raise ObjectNotFoundException(
                class_name="Image",
                statement="Invalid file type. Only images are allowed.",
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        image_data = await file.read()
        if not image_data:
            raise ObjectNotFoundException(
                class_name="Image",
                statement="Empty file uploaded.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        image_data_b64 = base64.b64encode(image_data).decode("utf-8")
        image = ImageCreate(file_name=file.filename, image_data=image_data_b64)

        async with unit_of_work:
            await unit_of_work.user.get_one(id=user_id)

            created_image = await unit_of_work.image.create(image)
            await unit_of_work.user.update({"image_id": created_image.id}, id=user_id)
        return created_image

    async def update(self, unit_of_work: UnitOfWork, user_id: int, file: UploadFile):
        if not file.content_type or not file.content_type.startswith("image/"):
            raise ObjectNotFoundException(
                class_name="Image",
                statement="Invalid file type. Only images are allowed.",
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        image_data = await file.read()
        if not image_data:
            raise ObjectNotFoundException(
                class_name="Image",
                statement="Empty file uploaded.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        image_data_b64 = base64.b64encode(image_data).decode("utf-8")
        image_update = ImageUpdate(file_name=file.filename, image_data=image_data_b64)

        async with unit_of_work:
            user = await unit_of_work.user.get_one(id=user_id)
            if user.image_id is None:
                raise ObjectNotFoundException(
                    class_name="Image",
                    statement=f"User {user_id} has no existing avatar to update",
                )
            await unit_of_work.image.update(image_update.model_dump(), id=user.image_id)
            return await unit_of_work.image.get_one(id=user.image_id)

    async def delete(self, user_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            user = await unit_of_work.user.get_one(id=user_id)

            if user.image_id is None:
                raise ObjectNotFoundException(
                    class_name="Image",
                    statement="User has no image to delete",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            image = await unit_of_work.image.get_one(id=user.image_id)

            await unit_of_work.user.update({"image_id": None}, id=user_id)

            await unit_of_work.image.delete(id=user.image_id)
            return image
