from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy_utils import database_exists, create_database

from social_network.main import app
from core.database import get_db, Base
from tests.utils.test_db import override_get_db, engine, TestingSessionLocal, SQLALCHEMY_TESTS_DATABASE_URL

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db():
    print('db вызван')
    if not database_exists(SQLALCHEMY_TESTS_DATABASE_URL):
        create_database(SQLALCHEMY_TESTS_DATABASE_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal


@pytest.fixture(scope="module")
def client():
    print('client вызван')
    with TestClient(app) as c:
        yield c
