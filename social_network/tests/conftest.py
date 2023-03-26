from typing import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import and_
from sqlalchemy_utils import database_exists, create_database

from apps.post import models as p_models
from apps.user import models, security
from social_network.main import app
from core.database import get_db, Base
from tests.utils.test_db import override_get_db, engine, TestingSessionLocal, SQLALCHEMY_TESTS_DATABASE_URL


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db():
    if not database_exists(SQLALCHEMY_TESTS_DATABASE_URL):
        create_database(SQLALCHEMY_TESTS_DATABASE_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def registered_user(db):
    session = db()
    hashed_password = security.get_password_hash('QwerTy1234#$')
    user = models.User(
        username='test_user2', email="example@mail.ru", password=hashed_password,
        is_active=False, uuid_to_activate=str(uuid4())
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(scope="session")
def active_user_with_post(db):
    session = db()
    hashed_password = security.get_password_hash('QwerTy1234#$')
    user = models.User(
        username='active_user', email="active_user@mail.ru", password=hashed_password,
        is_active=True, uuid_to_activate=str(uuid4())
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(scope="session")
def active_user_without_post(db):
    session = db()
    hashed_password = security.get_password_hash('QwerTy1234#$')
    user = models.User(
        username='active_user_without_post', email="active_user_wop@mail.ru", password=hashed_password,
        is_active=True, uuid_to_activate=str(uuid4())
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(scope="session")
def token(db, client):
    data = {
        "username": "active_user",
        "password": "QwerTy1234#$"
    }
    response = client.post('/users/login', data=data)

    return response.json()['access_token']


@pytest.fixture(scope="session")
def user_without_post_token(db, client):
    data = {
        "username": "active_user_without_post",
        "password": "QwerTy1234#$"
    }
    response = client.post('/users/login', data=data)

    return response.json()['access_token']


@pytest.fixture(scope='session')
def active_user_post(db, client, token):
    data = {
        "title": "active user post title",
        "content": "active user post content"
    }
    response = client.post('/posts', data=data, headers={"Authorization": f"Bearer {token}"})

    new_post = db().query(p_models.Post).get(response.json()['id'])

    return new_post


@pytest.fixture(scope="session")
def post_to_update(db, active_user_with_post):

    post_to_update = db().query(models.Post).filter(
        and_(
            models.Post.owner_id == active_user_with_post.id,
            models.Post.deleted == False
        )
    ).first()

    return post_to_update
