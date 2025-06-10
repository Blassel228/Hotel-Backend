from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials

from app.api.dependencies import auth_service_dep, UnitOfWorkDep
from app.schemas.user import UserGet

security = HTTPBearer()
router = APIRouter()


@router.post("/token/login/", summary="Login and Get Access Token")
async def login_for_access_token(
    service: auth_service_dep,
    unit_of_work: UnitOfWorkDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticate a user and generate an access token.
    """
    return await service.login_get_token(form_data=form_data, unit_of_work=unit_of_work)


@router.get("/user/me/", summary="Get Current User by Access Token")
async def get_current_user(
    service: auth_service_dep,
    unit_of_work: UnitOfWorkDep,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    """
    Retrieve the current user based on the provided JWT token.
    """
    return await service.get_current_user(
        unit_of_work=unit_of_work,
        token=credentials.credentials,
    )


@router.post("/user/credentials/", response_model=UserGet, summary="Get User by Username and Password")
async def get_user_by_credentials(
    service: auth_service_dep,
    unit_of_work: UnitOfWorkDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Retrieve a user directly using their username and password.
    """
    user = await service.authenticate_user(
        username=form_data.username, password=form_data.password, unit_of_work=unit_of_work
    )
    return UserGet(
        username=user.username,
        email=user.email,
        name=user.name,
        surname=user.surname,
        phone_number=user.phone_number,
        money_balance=user.money_balance,
    )
