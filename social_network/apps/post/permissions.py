
from ..user import schemas as user_schemas
from . import schemas


def post_owner(owner: user_schemas.User, post: schemas.Post):
    return post.owner_id == owner.id


def comment_owner(user: user_schemas.User, comment: schemas.Comment):
    return comment.owner_id == user.id
