from pydantic import BaseModel


class PasswordResetRequest(BaseModel):
    new_password: str
    token: str

class ForgotPasswordRequest(BaseModel):
    email: str

