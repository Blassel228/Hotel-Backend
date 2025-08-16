from fastapi import HTTPException, status


class ExistingValueException(HTTPException):
    """
    User tries to register entering existing data
    """

    def __init__(self, detail: dict[str, str]) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
