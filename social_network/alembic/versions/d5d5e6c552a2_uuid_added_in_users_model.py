"""uuid added in users model

Revision ID: d5d5e6c552a2
Revises: d25587f521b7
Create Date: 2023-03-19 17:37:46.351823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5d5e6c552a2'
down_revision = 'd25587f521b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('uuid_to_activate', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'uuid_to_activate')
    # ### end Alembic commands ###
