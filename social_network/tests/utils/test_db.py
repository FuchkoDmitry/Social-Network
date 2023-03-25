import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
PG__TEST_USER = os.environ.get('POSTGRES_TEST_USER')
PG_TEST_PASSWORD = os.environ.get('POSTGRES_TEST_PASSWORD')
PG_TEST_DB = os.environ.get('POSTGRES_TEST_DB')
PG_TEST_HOST = os.environ.get('POSTGRES_TEST_HOST', default='localhost')
PG_TEST_PORT = os.environ.get('POSTGRES_TEST_PORT')

SQLALCHEMY_TESTS_DATABASE_URL = (
    f"postgresql+psycopg2://{PG__TEST_USER}:{PG_TEST_PASSWORD}@{PG_TEST_HOST}:{PG_TEST_PORT}/{PG_TEST_DB}"
)

engine = create_engine(SQLALCHEMY_TESTS_DATABASE_URL, pool_pre_ping=True, echo=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
