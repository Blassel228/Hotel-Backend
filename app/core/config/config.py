from app.core.config.base import BaseConfig
from app.core.config.db import DataBaseConfig
from app.core.config.email_config import FastMailConfig
from app.core.config.stripe import StripeConfig
from app.enums import ExecutionMode


class Settings(BaseConfig):
    EXECUTION_MODE: ExecutionMode = ExecutionMode.TEST
    PROJECT_NAME: str = "hotel-backend"
    SERVER_HOST: str = "localhost"
    FRONTEND_URL: str = "http://localhost:5173/"
    REDIS_URL: str
    SERVER_PORT: int = 8000
    SERVER_CORS_ORIGINS: str = "*"
    DEBUG: bool = True

    ALGORITHM: str
    SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    stripe: StripeConfig = StripeConfig()

    db: DataBaseConfig = DataBaseConfig()

    fast_mail: FastMailConfig = FastMailConfig()

    @property
    def origins(self):
        return [origin.strip() for origin in self.SERVER_CORS_ORIGINS.split(",")]


settings = Settings()
