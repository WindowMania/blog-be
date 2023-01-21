from __future__ import annotations

import time
from typing import List, Optional
from datetime import datetime

import pydantic

from src.unit_of_work import SqlAlchemyUow
from src.post.models import Post
from src.post.repositories import PostDynamicCondition, TagStatistics


class NotFoundPost(Exception):
    def __init__(self):
        self.message = "존재 하지 않는 작성글"


class NotFoundTag(Exception):
    def __init__(self):
        self.message = '존재 하지 않는 태그'


class FailDeleteTag(Exception):
    def __init__(self, message):
        self.message = message


class PostDto(pydantic.BaseModel):
    id: str
    title: str
    body: str
    tags: List[str]
    username: str
    created_at: datetime
    updated_at: datetime
    deleted: bool

    @staticmethod
    def mapping(post: Post) -> Optional[PostDto]:
        if not post:
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
            deleted=post.deleted
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

    def get_tag_statistics(self) -> List[TagStatistics]:
        with self.uow:
            return self.uow.posts.get_tag_statistics()

    def delete_tag(self, tag: str):
        with self.uow:
            tag_model = self.uow.posts.get_tag(tag)
            if not tag_model:
                raise NotFoundTag()
            count = self.uow.posts.count_post_by_tag(tag)
            if count:
                raise FailDeleteTag(f"{count}개의 포스트가 존재 합니다.")
            self.uow.posts.delete(tag_model)
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

    def set_delete_post(self, post_id: str, deleted: bool) -> str:
        with self.uow:
            post = self.uow.posts.get(post_id)
            if not Post:
                raise NotFoundPost()
            post.set_deleted(deleted)
            self.uow.posts.add(post)
            self.uow.commit()
            return post.id

    def update_post(self, post_update_dto: PostUpdateDto):
        with self.uow:
            post = self.uow.posts.get(post_update_dto.id)
            if not post:
                raise NotFoundPost()
            post.update(
                title=post_update_dto.title,
                body=post_update_dto.body,
                tags=post_update_dto.tags
            )
            self.uow.posts.add(post)
            self.uow.commit()
            return PostDto.mapping(post)

    def get_post_dynamic_list(self, cond: PostDynamicCondition) -> List[PostDto]:
        with self.uow:
            posts = self.uow.posts.get_post_dynamic_list(cond)
            return [PostDto.mapping(post) for post in posts]


class PostTestService:

    def __init__(self, uow: SqlAlchemyUow):
        self.uow = uow

    def create_dummy_posts(self, writer_id: str):
        title = str(int(time.time()))
        print(title)
        body = "Lorem ipsum dolor sit amet, consectetur adipisicing elit. \n" \
               "Quos blanditiis tenetur unde suscipit, quam beatae rerum inventore consectetur, " \
               "neque doloribus, cupiditate numquam dignissimos laborum fugiat deleniti?\n Eum quasi quidem quibusdam."
        with self.uow:
            for i in range(100):
                new_post = Post(writer_id, str(i), body, ["All"])
                time.sleep(1)
                self.uow.posts.add(new_post)
                self.uow.commit()
