from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from social_network.apps.user import schemas as user_schemas
from social_network.apps.post import schemas, models


def get_owned_post(session: Session, owner: user_schemas.User, post_id: int):
    post = session.query(models.Post).get(post_id)
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    elif post.owner_id != owner.id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return post
