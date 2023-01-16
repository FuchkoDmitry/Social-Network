"""AddTables

Revision ID: d7af450f4ee3
Revises: 7bf5572953f3
Create Date: 2023-01-12 00:32:59.251356

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa

from social_network.apps.user.models import User

# revision identifiers, used by Alembic.
revision = 'd7af450f4ee3'
down_revision = '7bf5572953f3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('username', sa.String(length=50), nullable=False),
                    sa.Column('firstname', sa.String(length=30), nullable=True),
                    sa.Column('lastname', sa.String(length=40), nullable=True),
                    sa.Column('email', sa.String(length=80), nullable=False),
                    sa.Column('password', sa.String(length=100), nullable=False),
                    sa.Column('registration_at', sa.DateTime(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=True),
                    sa.Column('role', sqlalchemy_utils.types.choice.ChoiceType(User.ROLES), nullable=True),
                    sa.Column('photo', sa.String(length=100), nullable=True),
                    sa.Column('dob', sa.Date(), nullable=True),
                    sa.Column('gender', sqlalchemy_utils.types.choice.ChoiceType(User.GENDER), nullable=True),
                    sa.Column('is_open', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('followers',
                    sa.Column('follower_id', sa.Integer(), nullable=False),
                    sa.Column('followed_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
                    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
                    )
    op.create_table('post',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('title', sa.String(length=80), nullable=False),
                    sa.Column('content', sa.Text(), nullable=True),
                    sa.Column('image', sa.String(length=100), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('owner_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_post_title'), 'post', ['title'], unique=False)
    op.create_table('comment',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('content', sa.Text(), nullable=False),
                    sa.Column('owner_id', sa.Integer(), nullable=False),
                    sa.Column('post_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('parent_comment', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
                    sa.ForeignKeyConstraint(['parent_comment'], ['comment.id'], ),
                    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('like',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('post_id', sa.Integer(), nullable=False),
                    sa.Column('owner_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
                    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('repost',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('post_id', sa.Integer(), nullable=False),
                    sa.Column('owner_id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
                    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('repost')
    op.drop_table('like')
    op.drop_table('comment')
    op.drop_index(op.f('ix_post_title'), table_name='post')
    op.drop_table('post')
    op.drop_table('followers')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###