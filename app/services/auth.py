import logging
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt as jose_jwt, JWTError
from passlib.context import CryptContext

from app.core import settings
from app.models import User
from app.schemas.user import UserGet
from app.utils.unitofwork import UnitOfWork

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token/login/")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Service class for handling user authentication and token generation.
    """

    async def login_get_token(
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], unit_of_work: UnitOfWork
    ):
        user = await self.authenticate_user(
            username=form_data.username, password=form_data.password, unit_of_work=unit_of_work
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=20)
        access_token = self.create_access_token(
            data={"username": user.username, "email": user.email},
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}

    async def authenticate_user(self, username: str, password: str, unit_of_work: UnitOfWork):
        """
        Verify the user's credentials against the database.
        """
        async with unit_of_work:
            user = await unit_of_work.user.get_one(username=username)

        if not user or not pwd_context.verify(password, user.hashed_password):
            return False

        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        """
        Create an access token with an expiration time.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})

        encoded_jwt = jose_jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str):
        """
        Decode and validate an access token.
        """
        try:
            payload = jose_jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
            username: str = payload.get("username")
            user_id: int = payload.get("id")
            email: str = payload.get("email")
            if username is None or user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return {"username": username, "id": user_id, "email": email}
        except jose_jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jose_jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

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
            email: str = payload.get("email")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        async with unit_of_work:
            user: User = await unit_of_work.user.get_one(email=email)
        if user is None:
            raise credentials_exception

        return user


auth_service = AuthService()
