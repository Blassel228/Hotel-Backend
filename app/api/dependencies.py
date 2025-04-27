from typing import Annotated

from fastapi import Depends

from app.schemas.token import TokenData

from app.services.auth import auth_service
from app.services.auth import AuthService
from app.services.booking import BookingService
from app.services.property import PropertyService
from app.services.user import UserService
from app.utils.unitofwork import ABCUnitOfWork, UnitOfWork

UnitOfWorkDep = Annotated[ABCUnitOfWork, Depends(UnitOfWork)]

get_current_user = Annotated[TokenData, Depends(auth_service.get_current_user)]

property_service = Annotated[PropertyService, Depends(PropertyService)]
auth_service_dep = Annotated[AuthService, Depends(AuthService)]
user_service = Annotated[UserService, Depends(UserService)]
booking_service = Annotated[BookingService, Depends(BookingService)]
