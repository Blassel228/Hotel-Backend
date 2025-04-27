from fastapi import APIRouter

from app.api.dependencies import property_service, UnitOfWorkDep

router = APIRouter()


@router.get("")
async def get(service: property_service, unit_of_work: UnitOfWorkDep):
    return await service.get_all(unit_of_work)
