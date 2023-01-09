from datetime import datetime

import sqlalchemy as sq
from sqlalchemy.orm import relationship

from .database import Base


followers = sq.Table(
    'followers',
    Base.metadata,
    sq.Column('follower_id', sq.Integer, sq.ForeignKey('user.id'), primary_key=True),
    sq.Column('followed_id', sq.Integer, sq.ForeignKey('user.id'), primary_key=True)
)


class User(Base):

    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    username = sq.Column(sq.String(50), unique=True, nullable=False, index=True)
    email = sq.Column(sq.String(80), nullable=False, unique=True)
    password = sq.Column(sq.String(100), nullable=False)
    registration_at = sq.Column(sq.DateTime, default=datetime.now())
    is_active = sq.Column(sq.Boolean, default=False)
    is_admin = sq.Column(sq.Boolean, default=False)

    followed = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref='followers',
        lazy='dynamic'
        )

    posts = relationship('Post', back_populates="post_owner")
    comments = relationship('Comment', back_populates='comment_owner')
    liked_posts = relationship('Like', back_populates='like_owner')
    reposts = relationship('Repost', back_populates='repost_owner')


class Post(Base):

    __tablename__ = 'post'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    title = sq.Column(sq.String(80), nullable=False, index=True)
    content = sq.Column(sq.Text)
    image = sq.Column(sq.String(100))
    created_at = sq.Column(sq.DateTime, default=datetime.now())
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)

    post_owner = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post')
    post_likes = relationship('Like', back_populates='post_owner')
    reposts = relationship('Repost', back_populates='post')


class Comment(Base):
    __tablename__ = 'comment'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    content = sq.Column(sq.Text, nullable=False)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)
    post_id = sq.Column(sq.Integer, sq.ForeignKey('post.id'), nullable=False)
    created_at = sq.Column(sq.DateTime, default=datetime.now())
    parent_comment = sq.Column(sq.Integer, sq.ForeignKey('comment.id'), nullable=True)

    comment_owner = relationship('User', back_populates='comments')
    post = relationship('Post', backpopulates='comments')


class Like(Base):
    __tablename__ = 'like'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    post_id = sq.Column(sq.Integer, sq.ForeignKey('post.id'), nullable=False)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)
    created_at = sq.Column(sq.DateTime, default=datetime.now())

    like_owner = relationship('User', back_populates='liked_posts')
    post_owner = relationship('Post', back_populates='post_likes')


class Repost(Base):
    __tablename__ = 'repost'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    post_id = sq.Column(sq.Integer, sq.ForeignKey('post.id'), nullable=False)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)
    created_at = sq.Column(sq.DateTime, default=datetime.now())

    post = relationship('Post', back_populates='reposts')
    repost_owner = relationship('User', back_populates='reposts')
