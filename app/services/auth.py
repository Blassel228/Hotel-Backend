import hashlib
import logging
import secrets
from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import Depends, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt as jose_jwt, JWTError
from passlib.context import CryptContext

from app.core import settings
from app.core.exc import AuthError
from app.models import User
from app.schemas.token import TokenResponse, RefreshTokenCreate
from app.utils.unitofwork import UnitOfWork

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token/login/", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    async def get_current_user(self, token=Depends(oauth2_scheme), unit_of_work=Depends(UnitOfWork)):
        try:
            payload = jose_jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise AuthError(error_code="CREDENTIALS_INVALID", detail="Could not validate credentials")
        except JWTError:
            raise AuthError(error_code="CREDENTIALS_INVALID", detail="Could not validate credentials")

        async with unit_of_work:
            user: User = await unit_of_work.user.get_one(id=user_id)
        if user is None:
            raise AuthError(error_code="CREDENTIALS_INVALID", detail="Could not validate credentials")
        return user

    async def authenticate_user(self, username_or_email: str, password: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            user_by_username = await unit_of_work.user.get_one_or_none(username=username_or_email)
            user_by_email = await unit_of_work.user.get_one_or_none(email=username_or_email)
            user = user_by_username or user_by_email
        if not user or not pwd_context.verify(password, user.hashed_password):
            return False
        return user

    async def rotate_refresh_token(
            self, unit_of_work: UnitOfWork, refresh_token_str: str, response: Response
    ) -> TokenResponse:
        if not refresh_token_str:
            raise AuthError(error_code="REFRESH_TOKEN_MISSING", detail="Refresh token is required")

        hashed_token = hash_refresh_token(refresh_token_str)
        now = datetime.now(timezone.utc)

        async with unit_of_work:
            consumed = await unit_of_work.refresh_token.consume_token(
                token_hash=hashed_token,
                expires_after=now,
            )

            if not consumed:
                raise AuthError(
                    error_code="REFRESH_TOKEN_INVALID",
                    detail="Invalid, expired, or already used refresh token"
                )

            token_record = await unit_of_work.refresh_token.get_one_or_none(token_hash=hashed_token)
            if not token_record:
                raise AuthError(
                    error_code="REFRESH_TOKEN_INVALID",
                    detail="Token record missing after successful consumption"
                )

            new_refresh_value = secrets.token_urlsafe(64)
            new_refresh_expires = timedelta(seconds=30)

            new_refresh_token = RefreshTokenCreate(
                token_hash=hash_refresh_token(new_refresh_value),
                user_id=token_record.user_id,
                expires_at=datetime.now(timezone.utc) + new_refresh_expires,
                revoked=False,
                used=False,
            )
            await unit_of_work.refresh_token.create(new_refresh_token)

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], unit_of_work: UnitOfWork, response: Response
    ):
        user = await self.authenticate_user(form_data.username, form_data.password, unit_of_work)

        if not user:
            raise AuthError(
                error_code="INVALID_CREDENTIALS",
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(seconds=15)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email, "username": user.username},
            expires_delta=access_token_expires,
        )

        refresh_token_value = secrets.token_urlsafe(64)
        refresh_token_expires = timedelta(seconds=30)
        new_refresh_token = RefreshTokenCreate(
            token_hash=hash_refresh_token(refresh_token_value),
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + refresh_token_expires,
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
            max_age=int(refresh_token_expires.total_seconds()),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
        }

    async def logout_everywhere(self, current_user: User, unit_of_work: UnitOfWork):
        async with unit_of_work:
            await unit_of_work.refresh_token.revoke_all_for_user(current_user.id)
        return {"message": "All sessions revoked"}

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        expire_timestamp = int((datetime.now(timezone.utc) + expires_delta).timestamp())
        to_encode.update({"exp": expire_timestamp})
        return jose_jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)


auth_service = AuthService()