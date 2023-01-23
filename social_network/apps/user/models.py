from datetime import datetime

import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.choice import ChoiceType

from ..post.models import Post
from core.database import Base


followers = sq.Table(
    'followers',
    Base.metadata,
    sq.Column('follower_id', sq.Integer, sq.ForeignKey('user.id'), primary_key=True),
    sq.Column('followed_id', sq.Integer, sq.ForeignKey('user.id'), primary_key=True)
)


class User(Base):

    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User')
    ]
    GENDER = [
        ('male', 'male'),
        ('female', 'female')
    ]

    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    username = sq.Column(sq.String(50), unique=True, nullable=False, index=True)
    firstname = sq.Column(sq.String(30), nullable=True)
    lastname = sq.Column(sq.String(40), nullable=True)
    email = sq.Column(sq.String(80), nullable=False, unique=True)
    password = sq.Column(sq.String(100), nullable=False)
    registration_at = sq.Column(sq.DateTime, default=datetime.now())
    is_active = sq.Column(sq.Boolean, default=False)
    role = sq.Column(ChoiceType(ROLES), default='user')
    photo = sq.Column(sq.String(100))
    dob = sq.Column(sq.Date, nullable=True)
    gender = sq.Column(ChoiceType(GENDER), nullable=True)
    is_open = sq.Column(sq.Boolean, default=True)

    followed = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref='followers',
        lazy='dynamic'
        )

    posts = relationship(Post, back_populates="post_owner")
    comments = relationship('Comment', back_populates='comment_owner')
    liked_posts = relationship('Like', back_populates='like_owner')
    disliked_posts = relationship('Dislike', back_populates='dislike_owner')
    reposts = relationship('Repost', back_populates='repost_owner')

    def fullname(self):
        return f'{self.lastname.title()} {self.firstname.title()}'
