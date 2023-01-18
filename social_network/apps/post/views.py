from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from social_network.apps.post import schemas, crud, permissions
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


@router.delete('/{post_id}', status_code=204)
def delete_post(
        post_id: int,
        user: user_schemas.User = Depends(user_crud.get_current_user),
        db: Session = Depends(get_db)
):
    post = permissions.get_owned_post(db, user, post_id)
    crud.delete_post(db, post)
    return JSONResponse({"message": "deleted successfully"})
