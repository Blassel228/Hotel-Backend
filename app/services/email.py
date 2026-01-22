import os
import secrets
import ssl
from datetime import datetime, timedelta, timezone

import certifi
from fastapi import HTTPException
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail

from app.core import settings
import logging

from app.schemas.email import EmailIn
from app.utils.unitofwork import UnitOfWork

ssl_context = ssl.create_default_context(cafile=certifi.where())

fast_mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.fast_mail.MAIL_USERNAME,
    MAIL_PASSWORD=settings.fast_mail.MAIL_PASSWORD,
    MAIL_FROM=settings.fast_mail.MAIL_FROM,
    MAIL_SERVER=settings.fast_mail.MAIL_SERVER,
    MAIL_PORT=settings.fast_mail.MAIL_PORT,
    MAIL_STARTTLS=settings.fast_mail.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.fast_mail.MAIL_SSL_TLS,
)

logger = logging.getLogger(__name__)


class EmailService:
    async def verify_token(self, token: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            verification_token = await unit_of_work.verification_token.get_one_or_none(token=token)

            if not verification_token:
                raise HTTPException(status_code=400, detail="Invalid verification token")

            if verification_token.expires_at < datetime.now(timezone.utc):
                await unit_of_work.verification_token.delete(id=verification_token.id)
                raise HTTPException(status_code=400, detail="Verification token has expired")

            if verification_token.used:
                raise HTTPException(status_code=400, detail="Verification token already used")

            await unit_of_work.verification_token.update(
                {"used": True},
                id=verification_token.id
            )

            await unit_of_work.user.update(
                {"is_verified": True},
                id=verification_token.user_id
            )

        return {"message": "Email verified successfully!"}

    async def send_verification_email(self, user_id: str, unit_of_work: UnitOfWork):
        async with unit_of_work:
            user = await unit_of_work.user.get_one(id=user_id)

        if user.is_verified:
            return

        verification_token = secrets.token_urlsafe(64)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        token_data = {
            "token": verification_token,
            "user_id": user_id,
            "expires_at": expires_at,
            "used": False
        }

        async with unit_of_work:
            await unit_of_work.verification_token.create(token_data)

        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

        message = MessageSchema(
            subject="Підтвердіть ваш email",
            recipients=[user.email],
            body=f"""
            <h2>Підтвердіть ваш email</h2>
            <p>Натисніть кнопку нижче для підтвердження:</p>
            <a href="{verification_link}">Підтвердити email</a>
            <p>Посилання дійсне 15 хвилин.</p>
            """,
            subtype="html"
        )

        fm = FastMail(fast_mail_config)
        await fm.send_message(message)

    async def send_booking_confirmation_email(self, email: str, booking_data: EmailIn):
        os.environ['SSL_CERT_FILE'] = certifi.where()
        if not email:
            logger.warning("No email provided for booking confirmation")
            return

        start_date = booking_data.start_date.strftime("%d %B %Y")
        end_date = booking_data.end_date.strftime("%d %B %Y")
        booking_id = booking_data.id if booking_data.id else "N/A"

        html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #28a745;">✅ Бронювання підтверджено!</h2>
                <p>Привіт!</p>
                <p>Ваше бронювання успішно оплачено. Деталі:</p>
                <ul style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                    <li><strong>ID бронювання:</strong> {booking_id}</li>
                    <li><strong>Дата заїзду:</strong> {start_date}</li>
                    <li><strong>Дата виїзду:</strong> {end_date}</li>
                    <li><strong>Ціна:</strong> ${booking_data.price:.2f}</li>
                    <li><strong>Статус:</strong> Підтверджено</li>
                </ul>
                <p>Збережіть цей лист для подальших довідок.</p>
                <p>Дякуємо за довіру! Ми чекаємо на вас.</p>
                <hr>
                <p style="font-size: 12px; color: #6c757d;">
                    Це автоматичне повідомлення. Будь ласка, не відповідайте на нього.
                </p>
            </div>
            """

        try:
            message = MessageSchema(
                subject="✅ Ваше бронювання підтверджено",
                recipients=[email],
                body=html_body,
                subtype="html"
            )

            fm = FastMail(fast_mail_config)
            await fm.send_message(message)
            logger.info(f"Booking confirmation email sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send booking confirmation email to {email}: {str(e)}")