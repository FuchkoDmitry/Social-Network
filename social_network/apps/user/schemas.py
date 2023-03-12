import re
import logging
from datetime import date, datetime
from enum import Enum

from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
from pydantic import BaseModel, validator, Field, EmailStr
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_400_BAD_REQUEST

from ..post import schemas


schemas_logger = logging.getLogger(__name__)
schemas_logger.setLevel(logging.INFO)

handler = logging.FileHandler('logs/user_validation.log', mode='w')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')

handler.setFormatter(formatter)
schemas_logger.addHandler(handler)

schemas_logger.info('validation data')


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None


class UserToken(BaseModel):
    username: str
    email: str
    is_active: bool = False


class Gender(str, Enum):
    M = 'male'
    F = 'female'


class Role(str, Enum):
    admin = 'admin'
    user = 'user'


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    photo: str | None = None
    dob: date | None = Field(default=None, description='YYYY-MM-DD')
    gender: Gender | None = None


class User(UserBase):
    id: int

    class Config:
        orm_mode = True

    @validator("dob")
    def date_converter(cls, v):
        if v:
            return datetime.strftime(v, "%d-%m-%Y")


class CreateUser(UserBase):
    email: EmailStr
    password: str
    confirm_password: str
    firstname: str | None = Field(default=None, example='Ivan', max_length=30)
    lastname: str | None = Field(default=None, example='Ivanov', max_length=40)
    role: Role = Field(default='user')
    is_open: bool = Field(default=True, description='тип аккаунта')

    @validator('confirm_password')
    def password_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            schemas_logger.exception('passwords do not match')
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='passwords do not match'
            )
        schemas_logger.info('passwords matched')
        return v

    @validator('email')
    def email_validation(cls, v):
        try:
            validation = validate_email(v, check_deliverability=True)
            v = validation.email
            schemas_logger.info('email corrected')
        except EmailNotValidError as e:
            schemas_logger.exception(f'{str(e)}')
            print(str(e))
        return v

    @validator('dob')
    def birthdate_not_in_future_validation(cls, v):
        if v is not None:
            if v > date.today():
                schemas_logger.exception('Birthday can not be in future.')
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail='Birthday can not be in future.'
                )
        schemas_logger.info('DOB corrected')
        return v

    @validator('password', pre=True)
    def strong_password(cls, v):
        if re.search("^(?=(.*\d){2})(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z\d]).{,}$", v) is None:
            schemas_logger.exception('Your password is to easy.')
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Your password is to easy. Use lowercase and upper case letters, '
                'numbers and special characters(min 10 symbols)'
            )
        schemas_logger.info('Password corrected')
        return v


class Follower(UserBase):
    id: int

    class Config:
        orm_mode = True


# class Followed(UserBase):
class Followed(BaseModel):
    id: int

    class Config:
        orm_mode = True


class UserDetail(UserBase):
    id: int
    firstname: str | None
    lastname: str | None
    email: EmailStr | None
    posts: list[schemas.Post]
    reposts: list[schemas.Repost]
    followers: list[Follower]
    followed: list[Follower]

    class Config:
        orm_mode = True

    @validator("dob")
    def date_converter(cls, v):
        if v:
            return datetime.strftime(v, "%d-%m-%Y")
