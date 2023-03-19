from fastapi_mail import MessageSchema, MessageType
from pydantic import EmailStr

from core.email_conf import fast_mail


async def registration_email_task(email: EmailStr, uuid: str):
    message = MessageSchema(
        subject='Добро пожаловать!',
        recipients=[email],
        body=f'Для активации перейдите по ссылке: http://127.0.0.1:8000/users/activate/?uuid={uuid}',
        subtype=MessageType.plain
    )
    await fast_mail.send_message(message)
