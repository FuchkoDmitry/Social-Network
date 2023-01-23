from fastapi import HTTPException
from pydantic import BaseModel, Field, EmailStr, root_validator
from starlette.status import HTTP_400_BAD_REQUEST


class Like(BaseModel):
    owner_id: int

    class Config:
        orm_mode = True


class Dislike(Like):
    pass


class Repost(Like):
    pass


class Comment(Like):
    content: str


class BaseComment(BaseModel):
    content: str


class BasePost(BaseModel):
    id: int | None
    title: str = Field(..., max_length=80)
    content: str
    image: str | None


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

    class Config:
        orm_mode = True


class PostOwner(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class PostDetail(BasePost):
    post_owner: PostOwner
    comments: list[Comment]
    post_likes: list[Like]
    post_dislikes: list[Dislike]
    reposts: list[Repost]

    class Config:
        orm_mode = True


class PostCreate(BasePost):
    pass


class CreateComment(BaseComment):
    post_id: int
    content: str
