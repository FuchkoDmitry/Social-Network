from pydantic import BaseModel, Field


class Like(BaseModel):
    owner_id: int

    class Config:
        orm_mode = True


class Repost(Like):
    pass


class BaseComment(BaseModel):
    content: str


class Comment(BaseComment):
    owner_id: int

    class Config:
        orm_model = True


class BasePost(BaseModel):
    title: str = Field(..., max_length=80)
    content: str
    image: str | None


class Post(BasePost):
    owner_id: int

    # comments: list[Comment] | []
    post_likes: list[Like] | []
    # reposts: list[Repost] | []

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
