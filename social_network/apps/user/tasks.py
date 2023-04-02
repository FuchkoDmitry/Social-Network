from pydantic import EmailStr

from core.email_conf import send_email
from core.celery import celery


@celery.task
def activation_link_email_task(email: EmailStr, uuid: str):
    result = send_email(
        'Добро пожаловать!',
        [email],
        f'Для активации перейдите по ссылке: http://127.0.0.1:8000/users/activate/?uuid={uuid}',
    )
    return result


@celery.task
def account_activate_email_task(email: EmailStr, username: str):

    result = send_email(
        'Учетная запись активирована',
        [email],
        f'{username}, Вы успешно активировали свой аккаунт.',
    )
    return result
