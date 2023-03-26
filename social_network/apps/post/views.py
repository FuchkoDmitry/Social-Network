import shutil

from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
# from fastapi.openapi.models import Response
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST

from . import schemas, crud, permissions
from ..user import (
    schemas as user_schemas,
    crud as user_crud
)
from core.database import get_db

posts_router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    responses={404: {"description": "Not Found"}}
)

comments_router = APIRouter(
    prefix="/comments",
    tags=["Change/Delete comment"],
    responses={404: {"description": "Not Found"}}
)


@posts_router.post("/", response_model=schemas.Post, status_code=201)
def create_post(
        # user: user_schemas.User = Depends(user_crud.get_current_user),
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        title: str = Form(),
        content: str = Form(),
        image: UploadFile = File(default=None),
        db: Session = Depends(get_db)
):
    # post = schemas.PostCreate(title=title, content=content, owner_id=user.id)
    post = schemas.BasePost(title=title, content=content, owner_id=user.id)
    if image:
        with open(f'media/{user.username}_{image.filename}', 'wb') as buffer:
            shutil.copyfileobj(image.file, buffer)
        post.image = image.filename
    else:
        post.image = None
    return crud.create_post(db, post, user.id)


@posts_router.get("/", response_model=list[schemas.Post])
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_posts(db, skip, limit)


@posts_router.get("/{post_id}", response_model=schemas.PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post_details(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return post


@posts_router.delete('/{post_id}')
def delete_post(
        post_id: int,
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db)
):
    post = crud.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    is_owner = permissions.post_owner(user, post)
    if not is_owner:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)

    crud.delete_post(db, post)
    return JSONResponse({"message": "deleted successfully"}, status_code=204)


@posts_router.put('/{post_id}', status_code=200, response_model=schemas.Post)
def update_post(
        post_id: int,
        title: str = Form(),
        content: str = Form(),
        image: UploadFile = File(default=None),
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db)
):
    post = crud.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Post not found")

    is_owner = permissions.post_owner(user, post)
    if not is_owner:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden. It's not your post.")

    updated_post = schemas.BasePost(id=post.id, title=title, content=content)
    if image:
        with open(f'media/{user.username}_{image.filename}', 'wb') as buffer:
            shutil.copyfileobj(image.file, buffer)
        updated_post.image = image.filename
    else:
        updated_post.image = None

    crud.update_post(db, post_id, updated_post)
    return post


@posts_router.patch('/{post_id}', status_code=200, response_model=schemas.Post)
def partial_update_post(
        post_id: int,
        title: str = Form(default=None),
        content: str = Form(default=None),
        image: UploadFile = File(default=None),
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db)
):
    post = crud.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Post not found")

    is_owner = permissions.post_owner(user, post)
    if not is_owner:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden. It's not your post.")

    if image:
        with open(f'media/{user.username}_{image.filename}', 'wb') as buffer:
            shutil.copyfileobj(image.file, buffer)
        image = image.filename
    else:
        image = None

    updated_post = schemas.PostPartialUpdate(title=title, content=content, image=image)
    updated_post.id = post.id
    crud.partial_update_post(db, post_id, updated_post)
    return post


@posts_router.post(
    '/{post_id}/like',
    responses={400: {"description": "Forbidden. It's your post"}},
    name="Add/Remove like",
    status_code=201
)
def add_like(
        post_id: int,
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db),
):
    post = crud.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Post not found")
    is_owner = permissions.post_owner(user, post)
    if is_owner:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Forbidden. It's your post")
    crud.add_like(db, post_id, user.id)
    return JSONResponse({"message": "Success"}, status_code=201)


@posts_router.post(
    '/{post_id}/dislike',
    responses={400: {"description": "Forbidden. It's your post"}},
    name="Add/Remove dislike",
    status_code=201
)
def add_dislike(
        post_id: int,
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db)
):
    post = crud.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Post not found")
    is_owner = permissions.post_owner(user, post)
    if is_owner:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Forbidden. It's your post")
    crud.add_dislike(db, post_id, user.id)
    return JSONResponse({"message": "Success"}, status_code=201)


@posts_router.post(
    '/{post_id}/repost',
    responses={400: {"description": "Forbidden. It's your post"}},
    name="Repost the post",
    status_code=201
)
def post_repost(
        post_id: int,
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db)
):
    post = crud.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Post not found")
    is_owner = permissions.post_owner(user, post)
    if is_owner:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Forbidden. It's your post")
    crud.post_repost(db, post_id, user.id)
    return JSONResponse({"message": "Success"}, status_code=201)


@posts_router.post(
    '/{post_id}/comment',
    name="Add comment",
    status_code=201
)
def add_comment(
        post_id: int,
        content: schemas.AddComment,
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db)
):
    post = crud.get_post_by_id(db, post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Post not found")

    parent_comment = content.parent_comment
    if parent_comment is not None:
        parent_comment_exists = crud.comment_exists(db, parent_comment)
        if parent_comment_exists is None:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Parent comment not found")

    crud.add_comment(db, post_id, user.id, content)
    return JSONResponse({"success": "Your comment has been added"}, status_code=201)


@comments_router.put(
    '/{comment_id}',
    name="Delete Comment",
)
def delete_comment(
        comment_id: int,
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db)
):
    comment = crud.comment_exists(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    is_owner = permissions.comment_owner(user.id, comment.owner_id)
    if not is_owner:
        raise HTTPException(status_code=403, detail="It's not your comment")
    comment.deleted = True
    db.commit()
    return JSONResponse(content={"message": "Comment has been deleted"}, status_code=204)


@comments_router.patch(
    "/{comment_id}",
    name="Change comment",
    status_code=200,
    response_model=schemas.ChangeComment
)
def update_comment(
        comment_id: int,
        content: schemas.AddComment,
        user: user_schemas.User = Depends(user_crud.get_current_active_user),
        db: Session = Depends(get_db),
):
    comment = crud.comment_exists(db, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    is_owner = permissions.comment_owner(user.id, comment.owner_id)
    if not is_owner:
        raise HTTPException(status_code=403, detail="It's not your comment")
    comment.content = content.content

    db.commit()
    return comment
