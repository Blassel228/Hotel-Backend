from fastapi import APIRouter, UploadFile, File

from app.api.dependencies import image_service, UnitOfWorkDep, get_current_user

router = APIRouter()


@router.post("/")
async def create(service: image_service, unit_of_work: UnitOfWorkDep, current_user: get_current_user, file: UploadFile = File(...)):
    return await service.create(unit_of_work=unit_of_work, user_id=current_user.id, file=file)

@router.put("/")
async def update(service: image_service, unit_of_work: UnitOfWorkDep, current_user: get_current_user, file: UploadFile = File(...)):
    return await service.update(unit_of_work=unit_of_work, user_id=current_user.id, file=file)