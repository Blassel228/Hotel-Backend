from datetime import date

from fastapi import APIRouter, Depends

from app.api.dependencies import room_service, UnitOfWorkDep
from app.schemas.room import RoomFilterParams, RoomUpdate

router = APIRouter()


@router.get("")
async def get(service: room_service, unit_of_work: UnitOfWorkDep, offset: int = 0, limit: int = None):
    return await service.get_all(unit_of_work, offset, limit)


@router.get("/search/{start_date}/{end_date}/{capacity}")
async def search(unit_of_work: UnitOfWorkDep, start_date: date, end_date: date, capacity: int, service: room_service):
    return await service.search(unit_of_work=unit_of_work, start_date=start_date, end_date=end_date, capacity=capacity)


@router.get("/get_one/{room_id}")
async def get_one(room_id: str, unit_of_work: UnitOfWorkDep, service: room_service):
    return await service.get_one(room_id=room_id, unit_of_work=unit_of_work)

@router.put("/{room_id}")
async def update(room_id: str, unit_of_work: UnitOfWorkDep, service: room_service, room: RoomUpdate):
    return await service.update(room_id=room_id, unit_of_work=unit_of_work, room=room)

@router.get("/get_with_filters")
async def get_with_filters(
    unit_of_work: UnitOfWorkDep,
    service: room_service,
    filters: RoomFilterParams = Depends(),
):
    return await service.get_with_filters(
        unit_of_work=unit_of_work, filters=filters
    )
