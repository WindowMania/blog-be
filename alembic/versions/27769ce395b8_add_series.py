"""add_series

Revision ID: 27769ce395b8
Revises: f7dce763adde
Create Date: 2023-02-03 09:00:23.538016

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '27769ce395b8'
down_revision = 'f7dce763adde'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("series",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
                    sa.Column("user_id", sa.String(length=255), sa.ForeignKey("user.id"), nullable=False),
                    sa.Column("title", sa.String(length=255), nullable=False),
                    sa.Column("body", sa.TEXT(length=255), nullable=False))

    op.create_table("series_post",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(),
                              onupdate=sa.func.now()),
                    sa.Column("order_number", sa.Integer(), nullable=False),
                    sa.Column("post_id", sa.String(length=255), sa.ForeignKey("post.id"), nullable=False),
                    sa.Column("series_id", sa.String(length=255), sa.ForeignKey("series.id"), nullable=False)
                    )


def downgrade() -> None:
    op.drop_table("series_post")
    op.create_table("series")
