from fastapi import HTTPException, status


class InvalidGiftSelectedException(HTTPException):
    """
    User tries to send gift he does not own
    """

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class SendingGiftFailedException(HTTPException):
    """
    Sending gift fails
    """

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
