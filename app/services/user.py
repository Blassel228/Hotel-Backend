from pydantic import ValidationError, validate_email

from app.core.exc.user import ExistingValueException
from app.schemas.user import UserCreate, UserGet, UserUpdate, UserGetPartial
from app.services.auth import pwd_context
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


    async def update(self, user: UserUpdate, user_id: str, unit_of_work: UnitOfWork) -> UserGetPartial:
        async with unit_of_work:
            if user.username:
                existing = await unit_of_work.user.get_one_or_none(username=user.username)
                if existing and existing.id != user_id:
                    raise ExistingValueException(detail={"username": "Username is already taken"})

            if user.email:
                try:
                    validate_email(user.email)
                except ValidationError:
                    raise ExistingValueException(detail={"email": "Invalid email format"})

                existing = await unit_of_work.user.get_one_or_none(email=user.email)
                if existing and existing.id != user_id:
                    raise ExistingValueException(detail={"email": "Email is already registered"})

            if user.phone_number:
                existing = await unit_of_work.user.get_one_or_none(phone_number=user.phone_number)
                if existing and existing.id != user_id:
                    raise ExistingValueException(detail={"phone_number": "Phone number is already registered"})

        update_data = user.model_dump(exclude_none=True)

        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))

        async with unit_of_work:
            await unit_of_work.user.update(update_data, id=user_id)
            return await unit_of_work.user.get_one(id=user_id)

