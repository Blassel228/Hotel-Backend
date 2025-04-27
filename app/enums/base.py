from enum import StrEnum


class BaseStrEnum(StrEnum):
    @classmethod
    def list(cls) -> list["BaseStrEnum"]:
        return list(cls.__members__.values())


class ExecutionMode(BaseStrEnum):
    TEST = "test"
    PRODUCTION = "production"


class OrderDirection(BaseStrEnum):
    ASC = "asc"
    DESC = "desc"
