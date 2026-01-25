from fastapi import APIRouter, UploadFile, File

from app.api.dependencies import image_service, UnitOfWorkDep, get_current_user

router = APIRouter()


@router.post("/")
async def create(
    service: image_service, current_user: get_current_user, unit_of_work: UnitOfWorkDep, file: UploadFile = File(...)
):
    return await service.create(unit_of_work=unit_of_work, user_id=current_user.id, file=file)


@router.put("/")
async def update(
    service: image_service, unit_of_work: UnitOfWorkDep, current_user: get_current_user, file: UploadFile = File(...)
):
    return await service.update(unit_of_work=unit_of_work, user_id=current_user.id, file=file)


@router.put("/admin-update")
async def update(
    service: image_service, unit_of_work: UnitOfWorkDep, user_id: str, file: UploadFile = File(...)
):
    return await service.update(unit_of_work=unit_of_work, user_id=user_id, file=file)


@router.post("/admin-create")
async def create(
    service: image_service, user_id: str, unit_of_work: UnitOfWorkDep, file: UploadFile = File(...)
):
    return await service.create(unit_of_work=unit_of_work, user_id=user_id, file=file)


@router.get("/")
async def update(service: image_service, unit_of_work: UnitOfWorkDep, current_user: get_current_user):
    return await service.get_one(unit_of_work=unit_of_work, user_id=current_user.id)


@router.delete("/")
async def delete(service: image_service, unit_of_work: UnitOfWorkDep, current_user: get_current_user):
    return await service.delete(unit_of_work=unit_of_work, user_id=current_user.id)
