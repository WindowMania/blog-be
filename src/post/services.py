from typing import List

from src.unit_of_work import SqlAlchemyUow
from src.post.models import Post, Tag


class PostService:

    def __init__(self, uow: SqlAlchemyUow):
        self.uow = uow

    def upsert_tag(self, tag: str):
        with self.uow:
            self.uow.posts.upsert_tag(tag)
            self.uow.commit()

    def create_post(self, writer_id: str, title: str, body: str, tags: List[str]) -> str:
        with self.uow:
            new_post = Post(writer_id, title, body, tags)
            self.uow.posts.add(new_post)
            self.uow.commit()
            return new_post.id
