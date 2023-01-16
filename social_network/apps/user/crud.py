# from fastapi import Depends
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy import or_
from sqlalchemy.orm import Session
from starlette import status

# from . import models, schemas, security
from social_network.apps.user import models, schemas, security
# from social_network.apps.user.schemas import TokenData, UserToken
# from social_network.apps.user.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from social_network.db.database import get_db


# from models import User


# from schemas import CreateUser
# from security import get_password_hash, verify_password
# from ...db.database import get_db


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    users = db.query(models.User).offset(skip).limit(limit).all()
    for user in users:
        print(user.followers)
    return users


def user_exists(db: Session, email: str | None, username: str | None):
    return db.query(models.User).filter(or_(
        models.User.email == email,
        models.User.username == username
    )
    ).first()


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
    user = user_exists(db, email=None, username=username)
    if not user:
        return False
    if not security.verify_password(password, user.password):
        return False
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
    user = user_exists(db, username=token_data.username, email=None)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.UserToken = Depends(get_current_user)):
    if current_user.is_active:
        return current_user
    raise HTTPException(status_code=400, detail='подтвердите почту')

