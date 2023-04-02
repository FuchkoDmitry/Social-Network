import asyncio
import datetime

from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.orm import load_only

from apps.user import models
from core.database import SessionLocal
from core.email_conf import fast_mail
from core.celery import celery
from core.loggers import posts_logger


@celery.task
def add_reaction_to_post_email_task(post_owner_id: int, post_id: int, username: str):

    user = SessionLocal().query(models.User).options(load_only(models.User.email)).get(post_owner_id)

    message = MessageSchema(
        subject='Вашу запись оценили!',
        recipients=[user.email],
        body=f'Пользователь {username} оценил Ваш пост: http://127.0.0.1:8000/posts/{post_id}',
        subtype=MessageType.plain
    )

    result = fast_mail.send_message(message)
    asyncio.run(result)

    return {"status": "ok"}


@celery.task
def repost_email_task(post_owner_id: int, post_id: int, username: str):

    user = SessionLocal().query(models.User).options(load_only(models.User.email)).get(post_owner_id)

    message = MessageSchema(
        subject='Вашей записью поделились!',
        recipients=[user.email],
        body=f'Пользователь {username} поделился Вашей записью: http://127.0.0.1:8000/posts/{post_id}',
        subtype=MessageType.plain
    )

    result = fast_mail.send_message(message)
    asyncio.run(result)

    return {"status": "ok"}


@celery.task
def add_comment_to_post_email_task(post_owner_id: int, post_id: int, username: str, content: str):

    user = SessionLocal().query(models.User).options(load_only(models.User.email)).get(post_owner_id)

    message = MessageSchema(
        subject='Новый комментарий к Вашей записи!',
        recipients=[user.email],
        body=f'Пользователь {username} оставил комментарий: "{content}" к Вашей записи: http://127.0.0.1:8000/posts/{post_id}',
        subtype=MessageType.plain
    )

    result = fast_mail.send_message(message)
    asyncio.run(result)

    return {"status": "ok"}


@celery.task
def send_yesterday_posts():
    time_24_hours_ago = datetime.datetime.now() - datetime.timedelta(days=1)

    session = SessionLocal()
    users = session.query(models.User).options(load_only(models.User.email)).all()

    posts = session.query(models.Post).options(
        load_only(
            models.Post.title, models.Post.content, models.Post.created_at
        )).filter(
        models.Post.created_at >= time_24_hours_ago
    ).all()
    if posts:
        for user in users:
            message = MessageSchema(
                subject='новые посты вчера!',
                recipients=[user.email],
                body=f'Посты за вчера:\n {posts}',
                subtype=MessageType.plain
            )
            try:
                result = fast_mail.send_message(message)
                asyncio.run(result)
            except Exception as err:
                posts_logger.error(str(err))

        return {"result": f"Sent {len(users)} mail. {len(posts)} new posts"}
    return {"result": "no posts"}
