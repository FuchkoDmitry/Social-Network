
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload, lazyload, collections
from starlette import status

from . import models, schemas, security
from core.database import get_db
from core.loggers import users_logger


def get_user(db: Session, user_id: int):
    user = db.query(models.User).options(
        joinedload(models.User.posts),
        joinedload(models.User.reposts),
        joinedload(models.User.followers),
        joinedload(models.User.followed)
    ).filter(models.User.id == user_id).first()
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def user_exists(db: Session, username: str | None, email: str | None = None):
    if email:
        return db.query(models.User).filter(or_(
            models.User.username == username,
            models.User.email == email
        )).first()
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.CreateUser):
    user.password = security.get_password_hash(user.password)
    user = user.dict()
    user.pop('confirm_password')
    user = models.User(**user)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str):
    '''аутентификация по email?'''
    users_logger.info(f'user {username} try to login')
    user = user_exists(db, username=username)
    if not user:
        users_logger.warning(f'user {username} not exists!!')
        return False
    if not security.verify_password(password, user.password):
        users_logger.warning(f'user {username} login failure(incorrect password)')
        return False
    users_logger.info(f'user {username} login successfully')
    return user


async def get_current_user(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = user_exists(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.UserToken = Depends(get_current_user)):
    if current_user.is_active:
        return current_user
    raise HTTPException(status_code=400, detail='подтвердите почту')
