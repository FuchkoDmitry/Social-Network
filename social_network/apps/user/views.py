import asyncio
import shutil

from datetime import timedelta, date
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette import status
from fastapi_cache.decorator import cache

from . import schemas, crud, security, tasks, utils
from core.database import get_db
from core.loggers import users_logger

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)


@router.post('/', status_code=201)
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
    users_logger.info(
        f'User with username:{username} and email:{email} try to registration'
    )
    db_user = crud.user_exists(db, username, email)
    if db_user:
        users_logger.warning("user with this Email or username already registered")
        raise HTTPException(status_code=400, detail="user with this Email or username already registered")
    uuid = str(uuid4())
    user = schemas.CreateUser(
        username=username, dob=dob, gender=gender,
        email=email, password=password, confirm_password=confirm_password,
        firstname=firstname, lastname=lastname, uuid_to_activate=uuid
    )

    #  TODO: save photos in MongoDb
    if photo and 'image' in photo.content_type:
        with open(f'media/{username}_{photo.filename}', 'wb') as buffer:
            shutil.copyfileobj(photo.file, buffer)
        user.photo = photo.filename
    elif photo is None:
        user.photo = photo
    else:
        users_logger.warning("Incorrect photo type(image needed)")
        raise HTTPException(status_code=400, detail="Incorrect photo type(image needed)")
    #  проверка существует ли пароль через abstractapi
    # if not utils.valid_mail(email):
    #     user_views_logger.exception("Input a valid email address")
    #     raise HTTPException(status_code=400, detail="Input a valid email address")

    tasks.activation_link_email_task.apply_async(
        (user.email, uuid),
        retry=True,
        retry_policy={"max_retries": 3}
    )
    # tasks.registration_email_task.delay(user.email, uuid)



     # fastapi background_task
    # background_tasks.add_task(tasks.registration_email_task, user.email, uuid)

    users_logger.info(
        f'User with username:{username} and email:{email} registration successfully'
    )
    crud.create_user(db, user)
    return {"message": f"Congratulations! Your registration has been successfully. "
                       f"Activation link has been sent to {email}"
            }


@router.get("/activate/")
def activate_user(uuid: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_uuid(db, uuid)
    if user is None:
        raise HTTPException(status_code=400, detail="Bad URL")
    user.is_active = True
    db.commit()
    tasks.account_activate_email_task.delay(user.email, user.username)
    return {"message": f'User "{user.username}" with email "{user.email} activated successfully"'}


@router.get("/me/", response_model=schemas.UserDetail)
@cache(60)
async def read_users_me(current_user: schemas.UserDetail = Depends(crud.get_current_user)):
    return current_user


@router.get('/{user_id}', response_model=schemas.UserDetail)
@cache(expire=60)
def get_user(user_id: int, db: Session = Depends(get_db)):

    db_user = crud.get_user(db, user_id)

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get('/', response_model=list[schemas.User])
@cache(expire=120)
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
