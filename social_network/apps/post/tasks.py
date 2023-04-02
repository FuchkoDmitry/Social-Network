import datetime

from sqlalchemy.orm import load_only

from apps.user import models
from core.database import SessionLocal
from core.email_conf import send_email
from core.celery import celery


@celery.task
def add_reaction_to_post_email_task(post_owner_id: int, post_id: int, username: str):

    user = SessionLocal().query(models.User).options(load_only(models.User.email)).get(post_owner_id)

    result = send_email(
        'Вашу запись оценили!',
        [user.email],
        f'Пользователь {username} оценил Ваш пост: http://127.0.0.1:8000/posts/{post_id}'
    )
    return result


@celery.task
def repost_email_task(post_owner_id: int, post_id: int, username: str):

    user = SessionLocal().query(models.User).options(load_only(models.User.email)).get(post_owner_id)

    result = send_email(
        'Вашей записью поделились!',
        [user.email],
        f'Пользователь {username} поделился Вашей записью: http://127.0.0.1:8000/posts/{post_id}',
    )
    return result


@celery.task
def add_comment_to_post_email_task(post_owner_id: int, post_id: int, username: str, content: str):

    user = SessionLocal().query(models.User).options(load_only(models.User.email)).get(post_owner_id)

    result = send_email(
        'Новый комментарий к Вашей записи!',
        [user.email],
        body=f'Пользователь {username} оставил комментарий: '
             f'"{content}" к Вашей записи: http://127.0.0.1:8000/posts/{post_id}',
    )
    return result


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
            send_email(
                'новые посты вчера!',
                [user.email],
                f'Посты за вчера:\n {posts}',
            )

        return {"result": f"Sent {len(users)} mail. {len(posts)} new posts"}
    return {"result": "no posts"}
