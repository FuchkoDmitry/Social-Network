from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from social_network.apps.post import schemas, crud
from social_network.apps.user import (
    schemas as user_schemas,
    models as user_models,
    crud as user_crud
)
from social_network.core.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/", response_model=schemas.Post)
def create_post(
        post: schemas.PostCreate,
        user: user_schemas.User = Depends(user_crud.get_current_user),
        db: Session = Depends(get_db)):
    return crud.create_post(db, post, user.id)


@router.get("/", response_model=list[schemas.Post])
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_posts(db, skip, limit)
