from sqlalchemy.orm import Session, joinedload
from typing import List
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import func, desc
import sqlalchemy as sa

from src.post.models import Post, Tag, PostTag, Series, SeriesPost
from src.infra.repository import SqlAlchemyRepository
from pydantic import BaseModel


class PostDynamicCondition(BaseModel):
    page: int
    perPage: int
    deleted: bool
    tags: List[str]


class SeriesDynamicCondition(BaseModel):
    page: int
    perPage: int


class TagStatistics(BaseModel):
    tag: str
    count: int


class PostRepository(SqlAlchemyRepository):
    def __init__(self, session: Session):
        super().__init__(session, Post)

    def get_all_tags(self) -> List[Tag]:
        """
         태그 전체 불러오는 것, 캐싱 해야할 듯.
        """
        return self.session.query(Tag).all()

    def count_post_by_tag(self, tag: str) -> int:
        ret = self.session.query(func.count(PostTag.post_id)).filter(PostTag.tag_id == tag).first()
        return ret[0]

    def get_tag(self, tag: str) -> str:
        return self.session.query(Tag).filter(Tag.id == tag).first()

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
            .filter(~Post.deleted & Post.post_tags.any(PostTag.tag_id.in_(cond.tags)))

        return query \
            .order_by(desc(Post.created_at)) \
            .limit(cond.perPage) \
            .offset((cond.page - 1) * cond.perPage) \
            .all()

    def get_tag_statistics(self) -> List[TagStatistics]:
        ret = self.session.query(PostTag.tag_id, func.count(PostTag.id)) \
            .group_by(PostTag.tag_id) \
            .all()
        return [TagStatistics(tag=name, count=count) for name, count in ret]


class SeriesRepository(SqlAlchemyRepository):
    def __init__(self, session: Session):
        super().__init__(session, Series)

    def get_series_dynamic_list(self, cond: SeriesDynamicCondition):
        return self.session.query(Series) \
            .options(joinedload(Series.series_post_list)) \
            .order_by(desc(Series.created_at)) \
            .limit(cond.perPage) \
            .offset((cond.page - 1) * cond.perPage) \
            .all()
