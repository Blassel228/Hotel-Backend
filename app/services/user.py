import secrets
from uuid import UUID

import phonenumbers
from fastapi import HTTPException
from phonenumbers import NumberParseException
from pydantic import validate_email
from pydantic_core import PydanticCustomError

from app.core.exc.user import ExistingValueException
from app.core.redis import redis_client
from app.schemas.email import ChangeEmailRequest
from app.schemas.user import UserCreate, UserGet, UserUpdate, UserGetPartial
from app.services.auth import pwd_context
from app.services.email import EmailService
from app.utils.unitofwork import UnitOfWork


class UserService:
    async def get_multi(self, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.user.get_multi()

    async def get_one(self, unit_of_work: UnitOfWork, user_id: str):
        async with unit_of_work:
            return await unit_of_work.user.get_one(id=user_id)

    async def create(self, data: UserCreate, unit_of_work: UnitOfWork) -> UserGet:
        async with unit_of_work:
            user = await unit_of_work.user.get_one_or_none(username=data.username)
            if user:
                raise ExistingValueException(detail={"username": "Username is already taken"})

        async with unit_of_work:
            user = await unit_of_work.user.get_one_or_none(email=data.email)
            if user:
                raise ExistingValueException(detail={"email": "Email is already registered"})

        async with unit_of_work:
            user = await unit_of_work.user.get_one_or_none(phone_number=data.phone_number)
            if user:
                raise ExistingValueException(detail={"phone_number": "Phone number is already registered"})

        user_data = data.model_dump(exclude_none=True)
        hashed_password = pwd_context.hash(user_data.pop("password"))
        user_data["hashed_password"] = hashed_password

        async with unit_of_work:
            await unit_of_work.user.create(user_data)

        user_data.pop("hashed_password", None)
        return UserGet(**user_data)

    async def update(self, user: UserUpdate, user_id, unit_of_work: UnitOfWork) -> UserGetPartial:
        if isinstance(user_id, UUID):
            normalized_user_id = user_id
        else:
            normalized_user_id = UUID(str(user_id))

        async with unit_of_work:
            if user.username:
                existing = await unit_of_work.user.get_one_or_none(username=user.username)
                if existing and existing.id != normalized_user_id:
                    raise HTTPException(status_code=409, detail="Username is already taken")

            if user.phone_number:
                try:
                    parsed_number = phonenumbers.parse(user.phone_number, None)
                    if not phonenumbers.is_valid_number(parsed_number):
                        raise ValueError()
                except (NumberParseException, ValueError):
                    raise HTTPException(status_code=422, detail="Invalid phone number format")

                existing = await unit_of_work.user.get_one_or_none(phone_number=user.phone_number)
                if existing and existing.id != normalized_user_id:
                    raise HTTPException(status_code=409, detail="Phone number is already registered")

        update_data = user.model_dump(exclude_none=True)

        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))

        async with unit_of_work:
            await unit_of_work.user.update(update_data, id=normalized_user_id)
            return await unit_of_work.user.get_one(id=normalized_user_id)

    async def initiate_email_change(
        self,
        user_id: UUID,
        new_email: str,
        password: str,
        unit_of_work: UnitOfWork,
    ) -> str:
        try:
            validate_email(new_email)
        except PydanticCustomError:
            raise HTTPException(status_code=422, detail="Invalid email format")

        async with unit_of_work:
            user = await unit_of_work.user.get_one(id=user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

        if not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password")

        async with unit_of_work:
            existing = await unit_of_work.user.get_one_or_none(email=new_email)
            if existing:
                raise HTTPException(status_code=409, detail="Email is already registered")

        token = secrets.token_urlsafe(32)
        await redis_client.setex(f"email_change:{token}", 900, f"{user_id}:{new_email}")
        return token

    async def confirm_email_change(self, token: str, unit_of_work: UnitOfWork) -> UserGetPartial:
        data = await redis_client.get(f"email_change:{token}")
        if not data:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user_id, new_email = data.split(":")

        async with unit_of_work:
            await unit_of_work.user.update({"email": new_email}, id=UUID(user_id))
            updated_user = await unit_of_work.user.get_one(id=UUID(user_id))

        await redis_client.delete(f"email_change:{token}")

        return updated_user

    async def delete(self, user_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            await unit_of_work.user.delete(id=user_id)
            return await unit_of_work.user.get_one(id=user_id)
