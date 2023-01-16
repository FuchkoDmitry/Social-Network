from datetime import date, datetime
from enum import Enum

from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, validator, Field, EmailStr


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
            raise ValueError('passwords do not match')
        return v

    @validator('email')
    def email_validation(cls, v):
        try:
            validation = validate_email(v, check_deliverability=True)
            v = validation.email
        except EmailNotValidError as e:
            print(str(e))
        return v

    @validator('dob')
    def birthdate_not_in_future_validation(cls, v):
        if v > date.today():
            raise ValueError('Birthday can not be in future.')
        return v


class Follower(UserBase):
    class Config:
        orm_mode = True


class Followed(UserBase):
    class Config:
        orm_mode = True


class User(UserBase):
    # posts etc
    # posts: list[schemas.Post]
    # followers: list[Follower] = []
    # followed: list[Followed] = []
    # dob: str
    registration_at: datetime

    class Config:
        orm_mode = True

    @validator("dob")
    def date_converter(cls, v):
        if v:
            return datetime.strftime(v, "%d-%m-%Y")
