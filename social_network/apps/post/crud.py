from sqlalchemy.orm import Session
from social_network.apps.post import schemas, models
from social_network.apps.user import (
    schemas as user_schemas,
    models as user_models
)


def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    new_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()
