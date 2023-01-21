from pydantic import BaseModel, Field


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


class PostDetail(BasePost):
    comments: list[Comment]
    post_likes: list[Like]
    reposts: list[Repost]

    class Config:
        orm_mode = True


class PostCreate(BasePost):
    pass


class CreateLike(BaseModel):
    post_id: int  # привязать к посту


class CreateComment(BaseComment):
    post_id: int


class CreateRepost(CreateLike):
    pass
