from datetime import datetime

import sqlalchemy as sq
from sqlalchemy.orm import relationship, column_property

from core.database import Base


class Like(Base):
    __tablename__ = 'like'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    post_id = sq.Column(sq.Integer, sq.ForeignKey('posts.id'), nullable=False)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)
    created_at = sq.Column(sq.DateTime, default=datetime.now())

    like_owner = relationship('User', back_populates='liked_posts')
    post_owner = relationship('Post', back_populates='post_likes')


class Dislike(Base):
    __tablename__ = 'dislike'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    post_id = sq.Column(sq.Integer, sq.ForeignKey('posts.id'), nullable=False)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)
    created_at = sq.Column(sq.DateTime, default=datetime.now())

    dislike_owner = relationship('User', back_populates='disliked_posts')
    post_owner = relationship('Post', back_populates='post_dislikes')


class Comment(Base):
    __tablename__ = 'comment'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    content = sq.Column(sq.Text, nullable=False)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)
    post_id = sq.Column(sq.Integer, sq.ForeignKey('posts.id'), nullable=False, )
    created_at = sq.Column(sq.DateTime, default=datetime.now())
    parent_comment = sq.Column(sq.Integer, sq.ForeignKey('comment.id'), nullable=True)
    deleted = sq.Column(sq.Boolean, default=False)

    comment_owner = relationship('User', back_populates='comments')
    post = relationship('Post', back_populates='comments')

    child_comment = relationship('Comment', primaryjoin='Comment.parent_comment==Comment.id', uselist=True)


class Repost(Base):
    __tablename__ = 'repost'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    post_id = sq.Column(sq.Integer, sq.ForeignKey('posts.id'), nullable=False)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)
    created_at = sq.Column(sq.DateTime, default=datetime.now())

    post = relationship('Post', back_populates='reposts')
    repost_owner = relationship('User', back_populates='reposts')


class Post(Base):
    __tablename__ = 'posts'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    title = sq.Column(sq.String(80), nullable=False, index=True)
    content = sq.Column(sq.Text)
    image = sq.Column(sq.String(100))
    created_at = sq.Column(sq.DateTime, default=datetime.now())
    updated_at = sq.Column(sq.DateTime, nullable=True)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)
    deleted = sq.Column(sq.Boolean, default=False)

    # likes_count = column_property(
    #     sq.select([sq.func.count(Like.id)]).filter(Like.post_id == id).scalar_subquery()
    # )
    # dislikes_count = column_property(
    #     sq.select([sq.func.count(Dislike.id)]).filter(Dislike.post_id == id).scalar_subquery()
    # )
    # comments_count = column_property(
    #     sq.select([sq.func.count(Comment.id)]).filter(Comment.post_id == id).scalar_subquery()
    # )
    # reposts_count = column_property(
    #     sq.select([sq.func.count(Repost.id)]).filter(Repost.post_id == id).scalar_subquery()
    # )

    post_owner = relationship('User', back_populates='posts', lazy='joined')
    comments = relationship(Comment, back_populates='post', cascade='all,delete', order_by=Comment.created_at,
                            lazy='joined')
    post_likes = relationship(Like, back_populates='post_owner', cascade='all,delete', lazy='joined')
    post_dislikes = relationship(Dislike, back_populates='post_owner', cascade='all,delete', lazy='joined')
    reposts = relationship(Repost, back_populates='post', cascade='all,delete', lazy='joined')

    def __str__(self):
        return f'http://127.0.0.1:8000/posts/{self.id}. \n Title: {self.title}. \n Content: {self.content}\n'

    def __repr__(self):
        return f'http://127.0.0.1:8000/posts/{self.id}. \n Title: {self.title}. \n Content: {self.content}\n'
