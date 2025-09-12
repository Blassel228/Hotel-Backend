from typing import Annotated, Optional

from fastapi import Depends

from app.models import User
from app.schemas.token import TokenData

from app.services.auth import auth_service
from app.services.auth import AuthService
from app.services.booking import BookingService
from app.services.image import ImageService
from app.services.payment import PaymentService
from app.services.room import RoomService
from app.services.user import UserService
from app.services.guest import GuestService
from app.utils.unitofwork import ABCUnitOfWork, UnitOfWork

UnitOfWorkDep = Annotated[ABCUnitOfWork, Depends(UnitOfWork)]

get_current_user = Annotated[TokenData, Depends(auth_service.get_current_user)]

room_service = Annotated[RoomService, Depends(RoomService)]
auth_service_dep = Annotated[AuthService, Depends(AuthService)]
user_service = Annotated[UserService, Depends(UserService)]
booking_service = Annotated[BookingService, Depends(BookingService)]
guest_service = Annotated[GuestService, Depends(GuestService)]
image_service = Annotated[ImageService, Depends(ImageService)]
payment_service = Annotated[PaymentService, Depends(PaymentService)]
