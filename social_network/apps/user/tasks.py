import asyncio

from fastapi_mail import MessageSchema, MessageType
from pydantic import EmailStr

from core.email_conf import fast_mail
from core.celery import celery


@celery.task
def activation_link_email_task(email: EmailStr, uuid: str):
    message = MessageSchema(
        subject='Добро пожаловать!',
        recipients=[email],
        body=f'Для активации перейдите по ссылке: http://127.0.0.1:8000/users/activate/?uuid={uuid}',
        subtype=MessageType.plain
    )
    result = fast_mail.send_message(message)
    asyncio.run(result)

    return {"status": "ok"}


@celery.task
def account_activate_email_task(email: EmailStr, username: str):
    message = MessageSchema(
        subject='Учетная запись активирована',
        recipients=[email],
        body=f'{username}, Вы успешно активировали свой аккаунт.',
        subtype=MessageType.plain
    )
    result = fast_mail.send_message(message)
    asyncio.run(result)

    return {"status": "ok"}
