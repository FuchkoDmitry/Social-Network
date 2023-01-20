from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from social_network.apps.post import schemas, crud, permissions
from social_network.apps.user import (
    schemas as user_schemas,
    crud as user_crud
)
from social_network.core.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    responses={404: {"description": "Not Found"}}
)


@router.post("/", response_model=schemas.Post, status_code=201)
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
    post = crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    is_owner = permissions.post_owner(user, post)
    if not is_owner:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    crud.delete_post(db, post)
    return JSONResponse({"message": "deleted successfully"})


@router.put('/{post_id}', status_code=200, response_model=schemas.Post)
def update_post(
        post_id: int,
        updated_data: schemas.PostUpdate,
        user: user_schemas.User = Depends(user_crud.get_current_user),
        db: Session = Depends(get_db)
):
    post = crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    is_owner = permissions.post_owner(user, post)
    if not is_owner:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    crud.update_post(db, post_id, updated_data)
    return post


@router.patch('/{post_id}', status_code=200, response_model=schemas.Post)
def partial_update_post(
        post_id: int,
        updated_data: schemas.PostPartialUpdate,
        user: user_schemas.User = Depends(user_crud.get_current_user),
        db: Session = Depends(get_db)
):
    post = crud.get_post(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    is_owner = permissions.post_owner(user, post)
    if not is_owner:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    crud.partial_update_post(db, post_id, updated_data)
    return post
