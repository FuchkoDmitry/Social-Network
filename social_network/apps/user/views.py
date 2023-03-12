import shutil
import logging
from datetime import timedelta, date

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette import status

from . import schemas, crud, security, tasks, utils
from core.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)

#  создаем логгер и устанавливаем уровен логирования
user_views_logger = logging.getLogger(__name__)
user_views_logger.setLevel(logging.INFO)

#  настройка обработчика и форматировщика для логгера
handler = logging.FileHandler(f'logs/user_views.log', mode='w')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')

#  добавление форматировщика к обработчику
handler.setFormatter(formatter)
#  добавление обработчика к логгеру
user_views_logger.addHandler(handler)


@router.post('/', response_model=schemas.User)
def create_user(
        background_tasks: BackgroundTasks,
        username: str = Form(),
        photo: UploadFile = File(default=None),
        dob: date | None = Form(default=None),
        gender: schemas.Gender | None = Form(default=None),
        email: EmailStr = Form(),
        password: str = Form(),
        confirm_password: str = Form(),
        firstname: str | None = Form(default=None),
        lastname: str | None = Form(default=None),
        db: Session = Depends(get_db)
):
    user_views_logger.info(
        f'User with username:{username} and email:{email} try to registration'
    )
    db_user = crud.user_exists(db, username, email)
    if db_user:
        user_views_logger.exception("user with this Email or username already registered")
        raise HTTPException(status_code=400, detail="user with this Email or username already registered")

    user = schemas.CreateUser(
        username=username, dob=dob, gender=gender,
        email=email, password=password, confirm_password=confirm_password,
        firstname=firstname, lastname=lastname
    )

    #  TODO: save photos in MongoDb
    if photo and 'image' in photo.content_type:
        with open(f'media/{username}_{photo.filename}', 'wb') as buffer:
            shutil.copyfileobj(photo.file, buffer)
        user.photo = photo.filename
    elif photo is None:
        user.photo = photo
    else:
        user_views_logger.exception("Incorrect photo type(image needed)")
        raise HTTPException(status_code=400, detail="Incorrect photo type(image needed)")
    #  проверка существует ли пароль через abstractapi
    # if not utils.valid_mail(email):
    #     user_views_logger.exception("Input a valid email address")
    #     raise HTTPException(status_code=400, detail="Input a valid email address")
    background_tasks.add_task(tasks.registration_email_task, user.email)
    user_views_logger.info(
        f'User with username:{username} and email:{email} registration successfully'
    )
    return crud.create_user(db, user)


@router.get("/me/", response_model=schemas.UserDetail)
async def read_users_me(current_user: schemas.UserDetail = Depends(crud.get_current_user)):
    return current_user


@router.get('/{user_id}', response_model=schemas.UserDetail)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get('/', response_model=list[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}
