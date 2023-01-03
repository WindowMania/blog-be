"""add_user_status

Revision ID: 06170b30c1e2
Revises: f7dce763adde
Create Date: 2023-01-03 18:47:59.149508

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '06170b30c1e2'
down_revision = 'f7dce763adde'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("status", sa.String(255)))


def downgrade() -> None:
    op.drop_column("user", "status")
