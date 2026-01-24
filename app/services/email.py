import os
import ssl

import certifi
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail

from app.core import settings
import logging

from app.schemas.email import EmailIn

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
    async def send_verification_email_with_token(self, email: str, token: str):
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            body=f"""
            <h2>Confirm your email</h2>
            <p>Click the button below to complete your registration:</p>
            <a href="{verification_link}" style="display:inline-block; padding:10px 20px; background:#007bff; color:white; text-decoration:none; border-radius:5px;">
                Confirm email
            </a>
            <p>This link expires in 15 minutes.</p>
            """,
            subtype="html"
        )
        fm = FastMail(fast_mail_config)
        await fm.send_message(message)


    async def send_email_change_verification(self, new_email: str, token: str):
        verification_link = f"{settings.FRONTEND_URL}/verify-email-change?token={token}"
        message = MessageSchema(
            subject="Confirm your new email address",
            recipients=[new_email],
            body=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #007bff;">Confirm email change</h2>
                <p>You have requested to change your email address.</p>
                <p>Click the button below to confirm your new email:</p>
                <a href="{verification_link}" style="display:inline-block; padding:10px 20px; background:#007bff; color:white; text-decoration:none; border-radius:5px;">
                    Confirm new email
                </a>
                <p style="color: #dc3545; margin-top: 15px;">
                    ⚠️ If you didn't request this change, please ignore this email.
                </p>
                <p style="font-size: 12px; color: #6c757d;">
                    This link expires in 15 minutes.
                </p>
            </div>
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
                <h2 style="color: #28a745;">✅ Booking confirmed!</h2>
                <p>Hello!</p>
                <p>Your booking has been successfully paid. Details:</p>
                <ul style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                    <li><strong>Booking ID:</strong> {booking_id}</li>
                    <li><strong>Check-in date:</strong> {start_date}</li>
                    <li><strong>Check-out date:</strong> {end_date}</li>
                    <li><strong>Price:</strong> ${booking_data.price:.2f}</li>
                    <li><strong>Status:</strong> Confirmed</li>
                </ul>
                <p>Please save this email for your records.</p>
                <p>Thank you for your trust! We look forward to welcoming you.</p>
                <hr>
                <p style="font-size: 12px; color: #6c757d;">
                    This is an automated message. Please do not reply.
                </p>
            </div>
            """

        try:
            message = MessageSchema(
                subject="✅ Your booking is confirmed",
                recipients=[email],
                body=html_body,
                subtype="html"
            )

            fm = FastMail(fast_mail_config)
            await fm.send_message(message)
            logger.info(f"Booking confirmation email sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send booking confirmation email to {email}: {str(e)}")