import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
PG_USER = os.environ.get('POSTGRES_USER')
PG_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
PG_DB = os.environ.get('POSTGRES_DB')

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@localhost/{PG_DB}"

Base = declarative_base()
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()