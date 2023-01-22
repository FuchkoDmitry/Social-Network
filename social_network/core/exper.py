from datetime import date, datetime
from enum import Enum, IntEnum

from email_validator import validate_email, EmailNotValidError
from fastapi import UploadFile, File
from pydantic import BaseModel, ValidationError, validator, EmailStr, Field, FilePath


class Gender(str, Enum):
    M = 'male'
    F = 'female'

class Role(str, Enum):
    admin = 'admin'
    user = 'user'

class ToolEnum(IntEnum):
    spanner = 1
    wrench = 2


class CookingModel(BaseModel):
    gender: Gender | None = None
    tool: ToolEnum = ToolEnum.spanner


# class Gender(str, Enum):
#     male = 'male'
#     female = 'female'


class UserBase(BaseModel):
    username: str
    photo: str | None = None
    dob: date | None = None
    gender: Gender | None = None
    email: EmailStr
    role: Role = Field(default='user')

    @validator("dob", pre=True)
    def parse_birthdate(cls, value):
        '''
        привести строку с датой в формат date.
        обратный перевод: datetime.strftime(date(1988, 6, 28), "%d-%m-%Y")
        '''
        if isinstance(value, str):
            return datetime.strptime(
                value,
                "%d-%m-%Y"
            ).date()

    @validator('dob')
    def birthdate_not_in_future_validation(cls, v):
        if v > date.today():
            raise ValueError('Birthday can not be in future.')
        return v

    @validator('email')
    def email_validation(cls, v):
        try:
            validation = validate_email(v, check_deliverability=True)
            v = validation.email
        except EmailNotValidError as e:
            print(str(e))
        return v

u= UserBase(gender='female', username='username', dob='28-06-2020', email='dmitrii@mail.ru')
print(u.gender.name, u.email, u.image)
# print(CookingModel())
#> fruit=<FruitEnum.pear: 'pear'> tool=<ToolEnum.spanner: 1>
# print(CookingModel(tool=2, gender='male'))
#> fruit=<FruitEnum.banana: 'banana'> tool=<ToolEnum.wrench: 2>