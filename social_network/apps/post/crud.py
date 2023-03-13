from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, select

from . import schemas, models

from ..user import (
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
    return db.query(models.Post).filter(models.Post.deleted == False).order_by(
        desc(models.Post.created_at)).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(and_(
        models.Post.id == post_id,
        models.Post.deleted == False
    )).first()


def get_post_details(db: Session, post_id: int):
    # sq = db.query(models.Comment).filter(and_(
    #     models.Comment.parent_comment == None, models.Comment.post_id == post_id
    # )).subquery()
    #  for get only parent comments(without parent_comment attribute)
    sq = db.query(models.Comment).where(and_(
        models.Comment.parent_comment == None,
        models.Comment.post_id == post_id,
        models.Comment.deleted == False
    )
    ).all()

    post = db.query(models.Post).options(
        joinedload(models.Post.post_owner),
        joinedload(models.Post.comments),
        joinedload(models.Post.post_likes),
        joinedload(models.Post.post_dislikes),
        joinedload(models.Post.reposts),
    ).get(post_id)
    post.comments = sq
    return post


def delete_post(db: Session, post: schemas.Post):
    post.deleted = True
    # db.delete(post)
    db.commit()


def update_post(db: Session, post_id: int, updated_data: schemas.BasePost):
    db.query(models.Post).where(models.Post.id == post_id).update(
        {"updated_at": datetime.now(), **updated_data.dict()}
    )
    db.commit()


def partial_update_post(db: Session, post_id: int, updated_data: schemas.PostPartialUpdate):
    db.query(models.Post).where(models.Post.id == post_id).update(
        {"updated_at": datetime.now(), **updated_data.dict(exclude_unset=True)}
    )
    db.commit()


def reaction_exists(db: Session, post_id: int, user_id: int, model):
    return db.query(model).filter(
        model.post_id == post_id, model.owner_id == user_id
    ).first()


def add_like(db: Session, post_id: int, user_id: int):
    like = reaction_exists(db, post_id, user_id, models.Like)
    dislike = reaction_exists(db, post_id, user_id, models.Dislike)
    if like:
        db.delete(like)
    else:
        if dislike:
            db.delete(dislike)
        like = models.Like(post_id=post_id, owner_id=user_id)
        db.add(like)
    db.commit()


def add_dislike(db: Session, post_id: int, user_id: int):
    dislike = reaction_exists(db, post_id, user_id, models.Dislike)
    like = reaction_exists(db, post_id, user_id, models.Like)
    if dislike:
        db.delete(dislike)
    else:
        if like:
            db.delete(like)
        dislike = models.Dislike(post_id=post_id, owner_id=user_id)
        db.add(dislike)
    db.commit()


def post_repost(db: Session, post_id: int, user_id: int):
    repost = reaction_exists(db, post_id, user_id, models.Repost)
    if repost:
        db.delete(repost)
    else:
        repost = models.Repost(post_id=post_id, owner_id=user_id)
        db.add(repost)
    db.commit()


def add_comment(
        db: Session, post_id: int, user_id: int, content: schemas.BaseComment
):
    comment = models.Comment(**content.dict(), owner_id=user_id, post_id=post_id)
    db.add(comment)
    db.commit()

#  TODO: will add delete/update comment
# def delete_comment(
#         db: Session, user_id: int, comment_id: int
# ):
