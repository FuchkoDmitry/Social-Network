import os

from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab


load_dotenv()
BROKER_HOST = os.environ.get('REDIS_HOST', default='127.0.0.1')
BROKER_PORT = os.environ.get('REDIS_PORT', default='6379')

celery = Celery(
    'celery',
    broker=f'redis://{BROKER_HOST}:{BROKER_PORT}/0',
    backend=f'redis://{BROKER_HOST}:{BROKER_PORT}/1',
    include=['apps.user.tasks', 'apps.post.tasks']
)


celery.conf.beat_schedule = {
    'send-yesterday-posts': {
        'task': 'apps.post.tasks.send_yesterday_posts',
        'schedule': crontab(minute=15, hour=12)
    }
}
