"""added cover_img_url & description column to users table

Revision ID: f80790abd923
Revises: 4894995cce53
Create Date: 2022-08-12 13:50:06.757512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f80790abd923'
down_revision = '4894995cce53'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('description', sa.String(), server_default='default', nullable=False))
    op.add_column('users', sa.Column('cover_img_url', sa.String(), server_default='default', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'cover_img_url')
    op.drop_column('users', 'description')
    # ### end Alembic commands ###