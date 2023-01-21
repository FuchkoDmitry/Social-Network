
from pydantic import BaseModel, Field, EmailStr


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


class PostUpdate(BasePost):
    image: str


class PostPartialUpdate(BasePost):
    title: str | None = Field(max_length=80)
    content: str | None


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
