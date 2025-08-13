from app.core.exc.user import ExistingValueException
from app.schemas.user import UserCreate, UserGet
from app.services.auth import pwd_context
from app.utils.unitofwork import UnitOfWork


class UserService:
    async def get_multi(self, unit_of_work: UnitOfWork):
        async with unit_of_work:
            return await unit_of_work.user.get_multi()

    async def create(self, data: UserCreate, unit_of_work: UnitOfWork) -> UserGet:
        async with unit_of_work:
            user = await unit_of_work.user.get_one_or_none(username=data.username)
            if user:
                raise ExistingValueException(
                    detail={"username": "Username is already taken"}
                )

        async with unit_of_work:
            user = await unit_of_work.user.get_one_or_none(email=data.email)
            if user:
                raise ExistingValueException(
                    detail={"email": "Email is already registered"}
                )

        async with unit_of_work:
            user = await unit_of_work.user.get_one_or_none(phone_number=data.phone_number)
            if user:
                raise ExistingValueException(
                    detail={"phone_number": "Phone number is already registered"}
                )

        user_data = data.model_dump(exclude_none=True)
        hashed_password = pwd_context.hash(user_data.pop("password"))
        user_data["hashed_password"] = hashed_password

        async with unit_of_work:
            await unit_of_work.user.create(user_data)

        user_data.pop("hashed_password", None)
        return UserGet(**user_data)
