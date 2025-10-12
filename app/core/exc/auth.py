from typing import Optional

from fastapi import HTTPException


class AuthError(HTTPException):
    def __init__(
        self,
        error_code: str,
        detail: str,
        status_code: int = 401,
        headers: Optional[dict] = None
    ):
        self.error_code = error_code
        super().__init__(status_code=status_code, detail=detail, headers=headers)
