import logging
import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.user.models import UserEntity, UserCodeAuthentication
from src.post.models import Tag, PostTag, Post

logger = logging.getLogger(__name__)
metadata = sa.MetaData()

tag_table = sa.Table("tag", metadata,
                     sa.Column("id", sa.String(length=255), primary_key=True),
                     sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                     sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
                     )

post_table = sa.Table("post", metadata,
                      sa.Column("id", sa.String(length=255), primary_key=True),
                      sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                      sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
                      sa.Column("deleted", sa.Boolean, default=False),
                      sa.Column("user_id", sa.String(length=255), sa.ForeignKey("user.id"), nullable=False),
                      sa.Column("title", sa.String(length=255), nullable=False),
                      sa.Column("body", sa.String(length=255), nullable=False),
                      )

post_tag_table = sa.Table("post_tag", metadata,
                          sa.Column("id", sa.String(length=255), primary_key=True),
                          sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                          sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
                          sa.Column("post_id", sa.String(length=255), sa.ForeignKey("post.id"), nullable=False),
                          sa.Column("tag_id", sa.String(length=255), sa.ForeignKey("tag.id"), nullable=False),
                          )

user_table = sa.Table("user", metadata,
                      sa.Column("id", sa.String(length=255), primary_key=True),
                      sa.Column("account", sa.String(length=255), nullable=False, unique=True),
                      sa.Column("password", sa.String(length=255), nullable=False),
                      sa.Column("status", sa.String(length=255), nullable=False),
                      sa.Column("nick_name", sa.String(length=30), unique=True),
                      sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                      sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
                      )

user_code_authentication_table = sa.Table("user_code_authentication", metadata,
                                          sa.Column("id", sa.String(length=255), primary_key=True),
                                          sa.Column("user_id", sa.String(length=255), sa.ForeignKey("user.id")),
                                          sa.Column("method", sa.String(length=30), nullable=False),
                                          sa.Column("code", sa.String(length=30), nullable=False),
                                          sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                                          sa.Column("start_at", sa.DateTime(), nullable=False),
                                          sa.Column("end_at", sa.DateTime(), nullable=False),
                                          )


# https://docs.sqlalchemy.org/en/14/core/custom_types.html#sqlalchemy.types.TypeDecorator
# https://stackoverflow.com/questions/66537764/sqlalchemy-how-can-i-map-a-database-valuecolumn-to-my-value-object-class
# https://medium.com/pythonistas/i-like-lazy-relationships-do-you-sqlalchemy-relationship-loading-techniques-37d0fd43ac2

def start_mappers():
    logger.info("Starting mappers")
    user_code_authentication_mapper = orm.mapper(UserCodeAuthentication, user_code_authentication_table)
    tag_mapper = orm.mapper(Tag, tag_table)
    user_mapper = orm.mapper(
        UserEntity, user_table,
        properties={
            "code_authentication_list": orm.relationship(
                user_code_authentication_mapper,
            )
        }
    )
    post_tag_mapper = orm.mapper(PostTag, post_tag_table)

    post_mapper = orm.mapper(Post, post_table, properties={
        "user": orm.relationship(user_mapper, lazy="joined"),
        "post_tags": orm.relationship(post_tag_mapper, lazy="joined", cascade="all,delete-orphan")
    })
