"""init

Revision ID: f7dce763adde
Revises: 
Create Date: 2022-12-21 16:35:50.760097

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f7dce763adde'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("file",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("status", sa.String(length=255), nullable=False),
                    sa.Column("content_type", sa.String(length=255), nullable=False),
                    sa.Column("ext", sa.String(length=255), nullable=False),
                    sa.Column("origin_name", sa.String(length=255), nullable=False),
                    sa.Column("dir", sa.String(length=255), nullable=False),
                    sa.Column("size", sa.Integer(), nullable=False),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
                    )

    op.create_table("tag",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
                    )

    op.create_table("user",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("account", sa.String(length=255), nullable=False, unique=True),
                    sa.Column("password", sa.String(length=255), nullable=False),
                    sa.Column("nick_name", sa.String(length=30)),
                    sa.Column("status", sa.String(255)),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
                    )

    op.create_table("user_code_authentication",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("user_id", sa.String(length=255), sa.ForeignKey("user.id")),
                    sa.Column("method", sa.String(length=30), nullable=False),
                    sa.Column("code", sa.String(length=30), nullable=False),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("start_at", sa.DateTime(), nullable=False),
                    sa.Column("end_at", sa.DateTime(), nullable=False),
                    )

    op.create_table("post",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
                    sa.Column("deleted", sa.Boolean, default=False),
                    sa.Column("user_id", sa.String(length=255), sa.ForeignKey("user.id"), nullable=False),
                    sa.Column("title", sa.String(length=255), nullable=False),
                    sa.Column("body", sa.TEXT(), nullable=False),
                    )

    op.create_table("post_tag",
                    sa.Column("id", sa.String(length=255), primary_key=True),
                    sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                    sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
                    sa.Column("post_id", sa.String(length=255), sa.ForeignKey("post.id"), nullable=False),
                    sa.Column("tag_id", sa.String(length=255), sa.ForeignKey("tag.id"), nullable=False),
                    )


def downgrade() -> None:
    op.drop_table("post_tag")
    op.drop_table("post")
    op.drop_table("user_code_authentication")
    op.drop_table("user")
    op.drop_table('tag')
    op.drop_table('file')
