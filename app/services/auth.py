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


def ensure_utc_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


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
        hashed_token = hash_refresh_token(refresh_token_str)

        async with unit_of_work:
            token_record = await unit_of_work.refresh_token.get_one_or_none(
                token=hashed_token, revoked=False, used=False
            )

        if not token_record:
            raise AuthError(error_code="REFRESH_TOKEN_INVALID", detail="Invalid or revoked refresh token")

        now = datetime.now(timezone.utc)
        expires_at = ensure_utc_aware(token_record.expires_at)

        print(f"Now: {now}")
        print(f"Token expires at: {expires_at}")

        if expires_at < now:
            raise AuthError(error_code="REFRESH_TOKEN_EXPIRED", detail="Refresh token has expired")

        async with unit_of_work:
            await unit_of_work.refresh_token.update({"used": True, "revoked": True}, id=token_record.id)

            new_refresh_value = secrets.token_urlsafe(64)
            new_refresh_hashed = hash_refresh_token(new_refresh_value)
            new_refresh_expires = timedelta(minutes=45)
            new_refresh_token = RefreshTokenCreate(
                token=new_refresh_hashed,
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
            self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], unit_of_work: UnitOfWork,
            response: Response
    ):
        user = await self.authenticate_user(form_data.username, form_data.password, unit_of_work)

        if not user:
            raise AuthError(
                error_code="INVALID_CREDENTIALS",
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email, "username": user.username},
            expires_delta=access_token_expires,
        )

        refresh_token_value = secrets.token_urlsafe(64)
        refresh_token_hashed = hash_refresh_token(refresh_token_value)
        refresh_token_expires = timedelta(seconds=45)
        new_refresh_token = RefreshTokenCreate(
            token=refresh_token_hashed,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + refresh_token_expires,
            revoked=False,
            used=False,
        )
        print(f"Creating refresh token with expires_at: {new_refresh_token.expires_at}")
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
        expire_utc = datetime.now(timezone.utc) + expires_delta
        expire_timestamp = int(expire_utc.timestamp())
        to_encode.update({"exp": expire_timestamp})
        return jose_jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)


auth_service = AuthService()