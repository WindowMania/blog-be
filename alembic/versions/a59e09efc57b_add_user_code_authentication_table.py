"""add user_code_authentication_table

Revision ID: a59e09efc57b
Revises: 06170b30c1e2
Create Date: 2023-01-04 15:00:57.953317

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a59e09efc57b'
down_revision = '06170b30c1e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("user_code_authentication",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("user_id", sa.String(length=255), sa.ForeignKey("user.id")),
                    sa.Column("method", sa.String(length=30), nullable=False),
                    sa.Column("code", sa.String(length=30), nullable=False),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("start_at", sa.DateTime(), nullable=False),
                    sa.Column("end_at", sa.DateTime(), nullable=False),
                    )


def downgrade() -> None:
    op.drop_table("user_code_authentication")
