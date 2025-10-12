from app.core.config.base import BaseConfig


class StripeConfig(BaseConfig):
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_SUCCESS_URL: str
    STRIPE_CANCEL_URL: str
    STRIPE_WEBHOOK_SECRET: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
