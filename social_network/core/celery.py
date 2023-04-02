import os

from dotenv import load_dotenv
from celery import Celery


load_dotenv()
BROKER_HOST = os.environ.get('REDIS_HOST', default='127.0.0.1')
BROKER_PORT = os.environ.get('REDIS_PORT', default='6379')

celery = Celery(
    'celery',
    broker=f'redis://{BROKER_HOST}:{BROKER_PORT}/0',
    backend=f'redis://{BROKER_HOST}:{BROKER_PORT}/1',
    include=['apps.user.tasks', 'apps.post.tasks']
)
