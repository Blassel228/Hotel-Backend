from app.core.config.base import BaseConfig
from app.core.config.db import DataBaseConfig
from app.enums import ExecutionMode


class Settings(BaseConfig):
    EXECUTION_MODE: ExecutionMode = ExecutionMode.TEST
    PROJECT_NAME: str = "hotel-backend"
    SERVER_HOST: str = "localhost"
    SERVER_PORT: int = 8000
    SERVER_CORS_ORIGINS: str = "*"
    DEBUG: bool = True

    ALGORITHM: str
    SECRET: str

    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_SUCCESS_URL: str
    STRIPE_CANCEL_URL: str
    STRIPE_WEBHOOK_SECRET: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int

    db: DataBaseConfig = DataBaseConfig()

    @property
    def origins(self):
        return [origin.strip() for origin in self.SERVER_CORS_ORIGINS.split(",")]


settings = Settings()
