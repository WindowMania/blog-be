from __future__ import annotations
from typing import List, Optional
from datetime import datetime

import pydantic

from src.unit_of_work import SqlAlchemyUow
from src.post.models import Post, Tag


class NotFoundPost(Exception):
    def __init__(self):
        self.message = "존재 하지 않는 작성글"


class PostDto(pydantic.BaseModel):
    id: str
    title: str
    body: str
    tags: List[str]
    username: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def mapping(post: Post) -> Optional[PostDto]:
        if not Post:
            return None
        user = post.user

        return PostDto(
            id=post.id,
            title=post.title,
            body=post.body,
            tags=post.get_tag_id_list(),
            updated_at=post.updated_at,
            created_at=post.created_at,
            username=user.nick_name if user else 'unknown',
        )


class PostUpdateDto(pydantic.BaseModel):
    id: str
    title: Optional[str]
    body: Optional[str]
    tags: List[str]


class PostService:

    def __init__(self, uow: SqlAlchemyUow):
        self.uow = uow

    def upsert_tag(self, tag: str):
        with self.uow:
            self.uow.posts.upsert_tag(tag)
            self.uow.commit()

    def get_post(self, id: str) -> Optional[PostDto]:
        # post_tag 즉시 로딩 으로 가져올 것.
        with self.uow:
            ret = self.uow.posts.get(id)
            return PostDto.mapping(ret)

    def get_post_with_user(self, post_id: str) -> PostDto:
        with self.uow:
            post = self.uow.posts.get_with_user(post_id)
            if not post:
                raise NotFoundPost()

            return PostDto.mapping(post)

    def create_post(self, writer_id: str, title: str, body: str, tags: List[str]) -> str:
        with self.uow:
            new_post = Post(writer_id, title, body, tags)
            self.uow.posts.add(new_post)
            self.uow.commit()
            return new_post.id

    def update_post(self, post_update_dto: PostUpdateDto):
        with self.uow:
            post = self.uow.posts.get(post_update_dto.id)
            if not Post:
                raise NotFoundPost()
            post.update(
                title=post_update_dto.title,
                body=post_update_dto.body,
                tags=post_update_dto.tags
            )
            self.uow.posts.add(post)
            self.uow.commit()
            return PostDto.mapping(post)
