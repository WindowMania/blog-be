from sqlalchemy.orm import Session, joinedload
from typing import List
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import func, desc

from src.post.models import Post, Tag
from src.infra.repository import SqlAlchemyRepository
from pydantic import BaseModel


class PostDynamicCondition(BaseModel):
    page: int
    perPage: int
    deleted: bool


class PostRepository(SqlAlchemyRepository):
    def __init__(self, session: Session):
        super().__init__(session, Post)

    def get_all_tags(self) -> List[Tag]:
        """
         태그 전체 불러오는것, 캐싱 해야할 듯.
        """
        return self.session.query(Tag).all()

    def upsert_tag(self, tag: str):
        insert_stmt = insert(Tag).values(id=tag)
        on_duplicate_key_stmt = insert_stmt.on_duplicate_key_update(
            updated_at=func.current_timestamp(),
        )
        self.session.execute(on_duplicate_key_stmt)

    def get_with_user(self, post_id: str):
        return self.session.query(Post). \
            options(joinedload(Post.user), joinedload(Post.post_tags)). \
            filter_by(id=post_id). \
            first()

    def get_post_dynamic_list(self, cond: PostDynamicCondition):
        query = self.session.query(Post). \
            options(joinedload(Post.user), joinedload(Post.post_tags)) \
            .filter_by(deleted=cond.deleted)

        return query \
            .order_by(desc(Post.created_at)) \
            .limit(cond.perPage) \
            .offset((cond.page - 1) * cond.perPage) \
            .all()
