from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials

from app.api.dependencies import auth_service_dep, UnitOfWorkDep, get_current_user
from app.schemas.token import TokenResponse
from app.schemas.user import UserGet

security = HTTPBearer()
router = APIRouter()


@router.post("/token/login", response_model=TokenResponse)
async def login(
    unit_of_work: UnitOfWorkDep,
    auth_service: auth_service_dep,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return await auth_service.login_get_token(form_data=form_data, response=response, unit_of_work=unit_of_work)


@router.get("/user/me", summary="Get Current User by Access Token")
async def get_current_user_(
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


@router.post("/user/credentials", response_model=UserGet, summary="Get User by Username and Password")
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
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserGet(
        username=user.username,
        email=user.email,
        name=user.name,
        surname=user.surname,
        phone_number=user.phone_number,
        money_balance=user.money_balance,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    unit_of_work: UnitOfWorkDep,
    auth_service: auth_service_dep,
    response: Response,
    request: Request,
):
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    return await auth_service.rotate_refresh_token(unit_of_work, refresh_token_str, response)


@router.post("/logout-everywhere", response_model=dict[str, str])
async def logout_everywhere(
    current_user: get_current_user,
    unit_of_work: UnitOfWorkDep,
    auth_service: auth_service_dep,
    response: Response = None,
):
    result = await auth_service.logout_everywhere(current_user, unit_of_work)
    response.delete_cookie("refresh_token")
    return result
