from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, Field, EmailStr, root_validator, AnyUrl, validator
from starlette.status import HTTP_400_BAD_REQUEST


BASE_URL = "http://127.0.0.1:8000/"


class Like(BaseModel):
    owner_id: int

    class Config:
        orm_mode = True


class Dislike(Like):
    pass


class RepostPosts(BaseModel):
    post_id: int | AnyUrl

    class Config:
        orm_mode = True

    @validator("post_id")
    def convert_to_url(cls, v):
        return f'{BASE_URL}posts/{v}'


class RepostOwners(BaseModel):
    owner_id: int | AnyUrl

    class Config:
        orm_mode = True

    @validator("owner_id")
    def convert_to_url(cls, v):
        return f'{BASE_URL}users/{v}'


class ChangeComment(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True


class AddComment(BaseModel):
    '''добавление комментария'''
    content: str
    parent_comment: int | None = None


class DetailComment(BaseModel):
    '''отображение комментариев в детальном просмотре поста'''
    id: int
    content: str
    child_comment: list['DetailComment'] | None = None

    class Config:
        orm_mode = True


#  for get child comments(recursion)
DetailComment.update_forward_refs()


class BasePost(BaseModel):
    id: int | None
    title: str = Field(..., max_length=80)
    content: str
    image: str | None

    class Config:
        orm_mode = True


class PostPartialUpdate(BasePost):
    title: str | None = Field(max_length=80)
    content: str | None
    image: str | None

    @root_validator()
    def exclude_none_values(cls, field_values):
        field_values = {key: value for key, value in field_values.items() if value is not None}
        if not field_values:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You need to pass at least one value")
        return field_values


class Post(BasePost):
    owner_id: int
    likes_count: int
    dislikes_count: int
    comments_count: int
    reposts_count: int

    # class Config:
    #     orm_mode = True


class PostOwner(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class PostDetail(BasePost):
    post_owner: PostOwner
    comments: list[DetailComment]
    post_likes: list[Like]
    post_dislikes: list[Dislike]
    reposts: list[RepostOwners]

    class Config:
        orm_mode = True
