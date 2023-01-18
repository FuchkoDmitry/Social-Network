from fastapi_mail import MessageSchema, MessageType
from pydantic import EmailStr

from core.email_conf import fast_mail


async def registration_email_task(email: EmailStr):
    message = MessageSchema(
        subject='Добро пожаловать!',
        recipients=[email],
        body='uuid will be here later',
        subtype=MessageType.plain
    )
    await fast_mail.send_message(message)
