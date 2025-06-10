import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Sequence, Type, TypeVar

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    ColumnClause,
    Executable,
    Result,
    case,
    delete,
    func,
    insert,
    or_,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, joinedload

from app.core import settings
from app.core.exc import (
    DBConnectionException,
    ObjectExistsException,
    ObjectNotFoundException,
)
from app.enums import ExecutionMode, OrderDirection
from app.models.base import Base
from app.schemas.paginator import PaginatedOutput
from app.utils.paginator import paginate

ModelType = TypeVar("ModelType", bound=Base)
OperatorType = Callable[[Column, Any], ColumnClause]


action_map = {
    "gt": "__gt__",
    "lt": "__lt__",
    "ge": "__ge__",
    "le": "__le__",
    "in": "in_",
    "contains": "contains",
    "eq": "__eq__",
    "ne": "__ne__",
}


def get_obj_from_integrity_error(e: IntegrityError) -> str:
    if match := re.search(r"Key \((.*?)\)=\((.*?)\) already exists", str(e.orig)):
        return f"{match.group(1)}={match.group(2)}"
    return ""


class AbstractRepository(ABC, Generic[ModelType]):
    @abstractmethod
    async def get_one(self, **filters: Any) -> ModelType | None:
        raise NotImplementedError

    @abstractmethod
    async def get_multi(self, offset: int, limit: int | None = None, **filters: Any) -> Sequence[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, obj_in: BaseModel | dict[str, Any]) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        obj_in: BaseModel | dict[str, Any],
        *,
        return_object: bool = False,
        **filters: Any,
    ) -> int | ModelType:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, return_object: bool = False, **filters: Any) -> int | ModelType:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository, Generic[ModelType]):
    model: Type[ModelType]
    join_load_list: list[QueryableAttribute] = []

    def __init__(self, session: AsyncSession):
        self.literal_log: bool = settings.EXECUTION_MODE == ExecutionMode.TEST
        self.session = session
        self.model_name = self.model.__name__

    def _compile_statement(self, statement: Executable) -> Executable:
        """
        Compile statement

        Args:
            statement: statement

        Returns:
            Compiled statement
        """

        if self.literal_log:
            return statement.compile(compile_kwargs={"literal_binds": True})  # type:ignore[attr-defined]
        return statement

    async def execute(self, statement: Executable, action: Callable[[Any], Any] | None = None) -> Any:
        """
        Execute statement

        Args:
            statement: statement
            action: action

        Returns:
            Result of the statement

        """
        try:
            result: Result = await self.session.execute(statement)
            if action:
                result = action(result)
            return result
        except IntegrityError as e:
            if "duplicate" in str(e):
                raise ObjectExistsException(class_name=self.model_name, obj=get_obj_from_integrity_error(e)) from e
            raise e
        except NoResultFound as e:
            raise ObjectNotFoundException(
                class_name=self.model_name,
                statement=self._compile_statement(statement),
            ) from e
        except OSError as e:
            raise DBConnectionException(detail=str(e)) from e

    async def get_one(self, **filters: Any) -> ModelType:
        """
        Get one object

        Kwargs:
            filters: filters

        Returns:
            Object
        """

        statement = select(self.model).where(*self.get_where_clauses(filters))

        statement = self.add_loading_options(statement)
        return await self.execute(statement=statement, action=lambda result: result.unique().scalars().one())

    async def get_one_or_none(self, **filters: Any) -> ModelType:
        """
        Get one object or None

        Kwargs:
            filters: filters

        Returns:
            Object or None
        """

        statement = select(self.model).where(*self.get_where_clauses(filters))

        statement = self.add_loading_options(statement)
        return await self.execute(
            statement=statement,
            action=lambda result: result.unique().scalars().one_or_none(),
        )

    async def get_multi(self, offset: int = 0, limit: int | None = None, **filters: Any) -> Sequence[ModelType]:
        """
        Get multiple objects

        Args:
            offset: offset
            limit: limit

        Kwargs:
            filters: filters

        Returns:
            List of objects
        """

        statement = select(self.model).where(*self.get_where_clauses(filters)).offset(offset)

        if limit is not None:
            statement = statement.limit(limit)

        statement = self.add_loading_options(statement)
        return await self.execute(statement=statement, action=lambda result: result.unique().scalars().all())

    def get_where_clauses(self, filters: dict[str, Any]) -> list[ColumnClause]:
        """
        Get where clauses for statement

        Args:
            filters: dict with filters

        Raises:
            ValueError: if operator is not supported
            ValueError: if column is not found

        Returns:
            list of where clauses
        """
        clauses: list[ColumnClause] = []

        for key, value in filters.items():
            if "__" not in key:
                key = f"{key}__eq"

            column_name, action_name = key.split("__")

            column: Column = getattr(self.model, column_name, None)
            if column is None:
                raise ValueError(f"Invalid column {column_name} for {self.model_name}")

            action: str | None = action_map.get(action_name, None)
            if action is None:
                raise ValueError(
                    f"Unsupported action: {action_name}, supported actions: {', '.join(action_map.keys())}"
                )

            clause: ColumnClause = getattr(column, action)(value)
            clauses.append(clause)

        return clauses

    async def create(self, obj_in: BaseModel | dict[str, Any]) -> ModelType:
        """
        Create object

        Args:
            obj_in: object to create

        Returns:
            Created object
        """
        logger.debug(f"Creating {self.model_name}")

        data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
        statement = insert(self.model).values(**data).returning(self.model)

        statement = self.add_loading_options(statement)
        return await self.execute(statement=statement, action=lambda result: result.unique().scalar_one())

    async def update(
        self,
        obj_in: BaseModel | dict[str, Any],
        *,
        return_object: bool = False,
        **filters: Any,
    ) -> int | ModelType:
        """
        Update object

        Args:
            obj_in: object to update
            return_object: return updated object

        Kwargs:
            filters: filters

        Returns:
            Number of updated objects or object itself
        """
        logger.debug(f"Updating {self.model_name} with {filters=}")

        obj_in = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
        statement = update(self.model).where(*self.get_where_clauses(filters)).values(**obj_in)

        if return_object:
            statement = statement.returning(self.model)
            return await self.execute(statement=statement, action=lambda result: result.scalars().one())

        return await self.execute(statement=statement, action=lambda result: result.rowcount)

    async def delete(self, return_object: bool = False, **filters: Any) -> int | ModelType:
        """
        Delete object

        Args:
            return_object: return deleted object

        Kwargs:
            filters: filters

        Returns:
            Number of deleted objects or object itself
        """
        logger.debug(f"Deleting {self.model_name} with {filters=}")

        statement = delete(self.model).where(*self.get_where_clauses(filters))

        if return_object:
            statement = statement.returning(self.model)  # type:ignore
            statement = self.add_loading_options(statement)
            return await self.execute(statement=statement, action=lambda result: result.scalars().one())

        return await self.execute(statement=statement, action=lambda result: result.rowcount)

    async def get_count(self, **filters: Any) -> int:
        """
        Get count of objects

        Kwargs:
            filters: Filters

        Returns:
            Count of objects
        """

        statement = select(func.count(self.model.id)).where(*self.get_where_clauses(filters))

        return await self.execute(statement, action=lambda result: result.scalar())

    async def get_peak(self, column: str, f: Callable = func.max, **filters: Any) -> Any:
        """
        Get the peak value of a column based on filters and function
        Args:
            column: The column to find the maximum value for.
            filters: Filters to apply to the query.
        Returns:
            The maximum value of the specified column, or None if no rows match the filters.
        """
        statement = select(f(getattr(self.model, column))).where(*self.get_where_clauses(filters))

        max_value = await self.execute(statement=statement, action=lambda result: result.scalar())

        return max_value

    def add_loading_options(self, statement: Executable) -> Executable:
        for join_load in self.join_load_list:
            statement = statement.options(joinedload(join_load))
        return statement


class PaginateRepositoryMixin(Generic[ModelType]):
    model: Type[ModelType]
    session: AsyncSession
    get_where_clauses: Callable
    execute: Callable
    add_loading_options: Callable

    async def paged_list(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        order_by: str = "created_at",
        order_direction: OrderDirection = OrderDirection.DESC,
        **filters: Any,
    ) -> PaginatedOutput:
        statement = select(self.model).where(*self.get_filters(filters))
        statement = self.add_loading_options(statement)
        return await paginate(
            self,
            statement,
            page=page,
            per_page=per_page,
            order_by=order_by,
            order_direction=order_direction,
        )

    def get_filters(self, filters: dict) -> list:
        """
        Get filters for statement

        Args:
            filters: where clauses
        """
        search: str | None = filters.pop("search", None)
        search_fields: list | None = filters.pop("search_fields", None)

        where_clauses = self.get_where_clauses(filters)

        if search and search_fields:
            where_clauses.append(or_(func.upper(field).like(f"%{search.upper()}%") for field in search_fields))

        return where_clauses


class StatusSortingMixin(Generic[ModelType]):
    model: Type[ModelType]
    session: AsyncSession
    get_where_clauses: Callable
    execute: Callable
    add_loading_options: Callable

    async def get_multi_by_status(
        self,
        *,
        offset: int = 0,
        limit: int | None = None,
        status_priority: list[str] | None = None,
        **filters: Any,
    ) -> list[ModelType]:
        """
        Retrieve objects sorted by status and publish_date.

        Args:
            offset: Number of records to skip
            limit: Max number of records to return
            status_priority: List of statuses in desired priority order
            filters: Additional filters for the query

        Returns:
            List of sorted objects
        """
        if not status_priority:
            status_priority = [
                "published",
                "uploaded",
                "processing",
                "failed",
                "waiting",
            ]

        status_case = case(*[(self.model.status == status, index) for index, status in enumerate(status_priority)])

        statement = (
            select(self.model)
            .where(*self.get_where_clauses(filters))
            .order_by(status_case, self.model.publish_date.asc())
            .offset(offset)
        )

        if limit is not None:
            statement = statement.limit(limit)

        statement = self.add_loading_options(statement)
        return await self.execute(statement=statement, action=lambda result: result.unique().scalars().all())
