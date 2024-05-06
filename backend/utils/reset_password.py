from datetime import datetime, timedelta
from string import Template
from typing import Literal

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel

import config
from apps.web.models.auths import Auths
from apps.web.models.users import Users

from .utils import create_token, decode_token

# Define your email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_STARTTLS=config.MAIL_STARTTLS,
    MAIL_SSL_TLS=config.MAIL_SSL_TLS,
    USE_CREDENTIALS=config.MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=config.MAIL_VALIDATE_CERTS,
)


RESET_PASSWORD_MAIL_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Open WebUI Password Reset</title>
</head>
<body style="background-color: #f7f7f7; font-family: Arial, sans-serif; color: #333; margin: 0; padding: 20px;">
  <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
    <div style="background-color: #0056b3; color: #ffffff; padding: 10px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
      <h1>Open WebUI</h1>
    </div>
    <div style="padding: 20px;">
      <h2 style="color: #333;">Password Reset Request</h2>
      <p>Hello,</p>
      <p>You recently requested to reset your password for your Open WebUI account. To complete the process, please click the button below:</p>
      <a href="$reset_url" style="display: inline-block; padding: 10px 20px; margin-top: 20px; background-color: #28a745; color: #ffffff; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
      <p style="margin-top: 20px;">If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
    </div>
    <div style="font-size: 12px; color: #666; margin-top: 20px;">
      <p>&copy; $current_year Open WebUI.</p>
    </div>
  </div>
</body>
</html>
""")


class ResetToken(BaseModel):
    purpose: Literal["password_reset"]
    sub: str
    # This key prevents the token from being used more than once
    key: str


async def send_password_reset_mail(*, email: str, frontend_url: str) -> None:
    user = Users.get_user_by_email(email.lower())
    if user is None:
        return

    password_hash = Auths.get_hash_of_password(user.email)
    reset_token = create_token(
        data=ResetToken(
            purpose="password_reset", sub=user.id, key=password_hash
        ).model_dump(),
        expires_delta=timedelta(hours=1),
    )

    reset_url = f"{frontend_url}/auth/reset-password?token={reset_token}"
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[user.email],
        body=RESET_PASSWORD_MAIL_TEMPLATE.substitute(
            reset_url=reset_url, current_year=datetime.now().year
        ),
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)


def validate_password_reset_token(token: str) -> str:
    reset_token = ResetToken.model_validate(decode_token(token))

    user = Users.get_user_by_id(reset_token.sub)

    if user is None:
        raise ValueError("Invalid user")

    if reset_token.key != Auths.get_hash_of_password(user.email):
        raise ValueError("Invalid token key")

    return user.id
