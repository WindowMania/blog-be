import logging
import sqlalchemy as sa
import sqlalchemy.orm as orm

from src.user.aggregate.user import User

logger = logging.getLogger(__name__)
metadata = sa.MetaData()

user_table = sa.Table("user", metadata,
                      sa.Column("id", sa.String(length=255), primary_key=True),
                      sa.Column("account", sa.String(length=255), nullable=False, unique=True),
                      sa.Column("password", sa.String(length=255), nullable=False),
                      sa.Column("nick_name", sa.String(length=30), unique=True),
                      sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                      sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
                      )


# https://docs.sqlalchemy.org/en/14/core/custom_types.html#sqlalchemy.types.TypeDecorator
# https://stackoverflow.com/questions/66537764/sqlalchemy-how-can-i-map-a-database-valuecolumn-to-my-value-object-class


def start_mappers():
    logger.info("Starting mappers")
    user_mapper = orm.mapper(User, user_table)
