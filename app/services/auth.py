import logging
import secrets
from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.openapi.models import Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt as jose_jwt, JWTError
from passlib.context import CryptContext

from app.core import settings
from app.models import User
from app.schemas.token import TokenResponse, RefreshTokenCreate
from app.utils.unitofwork import UnitOfWork

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token/login/", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Service class for handling user authentication and token generation.
    """

    async def get_current_user(self, token=Depends(oauth2_scheme), unit_of_work=Depends(UnitOfWork)):
        """
        Retrieve the current user based on the provided JWT token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

        try:
            payload = jose_jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
            id: str = payload.get("sub")
            if id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        async with unit_of_work:
            user: User = await unit_of_work.user.get_one(id=id)
        if user is None:
            raise credentials_exception

        return user


    async def authenticate_user(self, username: str, password: str, unit_of_work: UnitOfWork):
        """
        Verify the user's credentials against the database.
        """
        async with unit_of_work:
            user = await unit_of_work.user.get_one_or_none(username=username)

        if not user or not pwd_context.verify(password, user.hashed_password):
            return False

        return user

    async def rotate_refresh_token(
            self,
            unit_of_work: UnitOfWork,
            refresh_token_str: str,
            response: Response
    ) -> TokenResponse:
        async with unit_of_work:
            token_record = await unit_of_work.refresh_token.get_one_or_none(token=refresh_token_str, revoked=False, used=False)

        if not token_record:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if token_record.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
            raise HTTPException(status_code=401, detail="Refresh token expired")

        async with unit_of_work:

            await unit_of_work.refresh_token.update({"used": True, "revoked": True}, id=token_record.id)

            new_refresh_value = secrets.token_urlsafe(64)
            new_refresh_expires = timedelta(seconds=15)

            new_refresh_token = RefreshTokenCreate(
                token=new_refresh_value,
                user_id=token_record.user_id,
                expires_at=(datetime.now(timezone.utc) + new_refresh_expires).replace(tzinfo=None),
                revoked=False,
                used=False,
            )

            await unit_of_work.refresh_token.create(new_refresh_token)

            access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": str(token_record.user_id)},
                expires_delta=access_token_expires,
            )

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_value,
            httponly=True,
            secure=False,
            samesite="strict",
            max_age=int(new_refresh_expires.total_seconds()),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_value,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
        )


    async def login_get_token(
        self,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        unit_of_work: UnitOfWork,
        response: Response
    ):
        """
        Генерує access_token + refresh_token після успішного логіну.
        """
        user = await self.authenticate_user(form_data.username, form_data.password, unit_of_work)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(seconds=15)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email, "username": user.username},
            expires_delta=access_token_expires,
        )

        refresh_token_value = secrets.token_urlsafe(64)
        refresh_token_expires = timedelta(seconds=15)

        new_refresh_token = RefreshTokenCreate(
            token=refresh_token_value,
            user_id=user.id,
            expires_at=(datetime.now(timezone.utc) + refresh_token_expires).replace(tzinfo=None),
            revoked=False,
            used=False,
        )

        async with unit_of_work:
            await unit_of_work.refresh_token.create(new_refresh_token)

        logger.info(f"User {user.email} logged in successfully")

        response.set_cookie(
            key="refresh_token",
            value=refresh_token_value,
            httponly=True,
            secure=False,
            samesite="strict",
            max_age=60,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
        }

    async def logout_everywhere(
        self,
        current_user: User,
        unit_of_work: UnitOfWork
    ):
        async with unit_of_work:
            await unit_of_work.refresh_token.revoke_all_for_user(current_user.id)
        return {"message": "All sessions revoked"}

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        """
        Create an access token with an expiration time.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})

        encoded_jwt = jose_jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)
        return encoded_jwt

auth_service = AuthService()