import json
from datetime import date

from fastapi import APIRouter, Depends, Form, File, UploadFile

from app.api.dependencies import room_service, UnitOfWorkDep, get_current_user
from app.schemas.room import RoomFilterParams, RoomCreateIn, RoomUpdateIn

router = APIRouter()


@router.get("/")
async def get(service: room_service, unit_of_work: UnitOfWorkDep, offset: int = 0, limit: int = None):
    return await service.get_all(unit_of_work, offset, limit)


@router.post("/")
async def create(
    unit_of_work: UnitOfWorkDep, service: room_service, room: str = Form(...), image: UploadFile = File(...)
):
    room_dict = json.loads(room)
    room = RoomCreateIn(**room_dict)
    image = await image.read()
    return await service.create(unit_of_work=unit_of_work, room=room, image=image)


@router.get("/search/{start_date}/{end_date}/{capacity}")
async def search(unit_of_work: UnitOfWorkDep, start_date: date, end_date: date, capacity: int, service: room_service):
    return await service.search(unit_of_work=unit_of_work, start_date=start_date, end_date=end_date, capacity=capacity)


@router.get("/{room_id}")
async def get_one(room_id: str, unit_of_work: UnitOfWorkDep, service: room_service):
    return await service.get_one(room_id=room_id, unit_of_work=unit_of_work)


@router.put("/{room_id}")
async def update(room_id: str, unit_of_work: UnitOfWorkDep, service: room_service, room: RoomUpdateIn):
    return await service.update(room_id=room_id, unit_of_work=unit_of_work, room=room)


@router.delete("/{room_id}")
async def update(room_id: str, unit_of_work: UnitOfWorkDep, service: room_service):
    return await service.delete(room_id=room_id, unit_of_work=unit_of_work)


@router.get("/filter", summary="Get rooms using filter parameters")
async def get_filtered_rooms(
    unit_of_work: UnitOfWorkDep,
    service: room_service,
    filters: RoomFilterParams = Depends(),
):
    return await service.get_with_filters(unit_of_work=unit_of_work, filters=filters)


@router.get("/not-rated", summary="Get rooms booked but not rated by the user")
async def get_not_rated_rooms(
    unit_of_work: UnitOfWorkDep,
    service: room_service,
    current_user: get_current_user,
):
    return await service.get_rooms_booked_not_rated_by_user(unit_of_work=unit_of_work, user_id=current_user.id)