from app.core.config.base import BaseConfig


class FastMailConfig(BaseConfig):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: str
    MAIL_STARTTLS: str
    MAIL_SSL_TLS: str

