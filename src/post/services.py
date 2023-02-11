from __future__ import annotations

import time
from typing import List, Optional, Tuple, Union
from datetime import datetime

import pydantic

from src.unit_of_work import SqlAlchemyUow
from src.post.models import Post, Series, SeriesPost
from src.post.repositories import PostDynamicCondition, TagStatistics, SeriesDynamicCondition


class NotFoundPost(Exception):
    def __init__(self):
        self.message = "존재 하지 않는 작성글"


class NotFoundSeries(Exception):
    def __init__(self):
        self.message = "존재 하지 않는 시리즈"


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


class SeriesPostDto(pydantic.BaseModel):
    id: str
    post_id: str
    series_id: str
    order_number: int

    @staticmethod
    def mapping(s: SeriesPost) -> SeriesPostDto:
        return SeriesPostDto(id=s.id,
                             post_id=s.post_id,
                             series_id=s.series_id,
                             order_number=s.order_number
                             )

    def set_order_number(self, num: int):
        self.order_number = num


class SeriesPostWithPostDto(pydantic.BaseModel):
    id: str
    post_id: str
    series_id: str
    order_number: int
    post: PostDto

    @staticmethod
    def mapping(s: SeriesPost) -> SeriesPostDto:
        return SeriesPostWithPostDto(id=s.id,
                                     post_id=s.post_id,
                                     series_id=s.series_id,
                                     order_number=s.order_number,
                                     post=PostDto.mapping(s.post)
                                     )


class SeriesDto(pydantic.BaseModel):
    id: str
    title: str
    body: str
    series_post_list: List[Union[SeriesPostWithPostDto, SeriesPostDto]]
    user_id: str
    updated_at: str
    created_at: str

    @staticmethod
    def mapping(s: Series) -> SeriesDto:
        sorted_post_list = sorted(s.series_post_list, key=lambda sp: sp.order_number)
        return SeriesDto(id=s.id,
                         title=s.title,
                         body=s.body,
                         user_id=s.user_id,
                         series_post_list=[SeriesPostDto.mapping(ps) for ps in sorted_post_list],
                         updated_at=str(s.updated_at),
                         created_at=str(s.created_at)
                         )

    @staticmethod
    def mapping_with_post(s: Series) -> SeriesDto:
        sorted_post_list = sorted(s.series_post_list, key=lambda sp: sp.order_number)
        return SeriesDto(id=s.id,
                         title=s.title,
                         body=s.body,
                         user_id=s.user_id,
                         series_post_list=[SeriesPostWithPostDto.mapping(ps) for ps in sorted_post_list],
                         updated_at=str(s.updated_at),
                         created_at=str(s.created_at)
                         )

    def get_post_id_and_order(self) -> List[Tuple[int, str]]:
        ret = []
        for s in self.series_post_list:
            ret.append((s.order_number, s.post_id))
        ret.sort()
        return ret


class PostUpdateDto(pydantic.BaseModel):
    id: str
    title: Optional[str]
    body: Optional[str]
    tags: List[str]


class SeriesUpdateDto(pydantic.BaseModel):
    id: str
    title: Optional[str]
    body: Optional[str]
    # series_post_list: List[SeriesPostDto]
    series_post_list: List[str]


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


class SeriesService:
    def __init__(self, uow: SqlAlchemyUow):
        self.uow = uow

    def create_series(self, user_id: str, title: str, body: str, post_id_list: List[str] = []) -> str:
        with self.uow:
            new_series = Series(user_id=user_id, title=title, body=body, post_id_list=post_id_list)
            self.uow.series.add(new_series)
            self.uow.commit()
            return new_series.id

    def find_series(self, series_id: str) -> SeriesDto:
        with self.uow:
            found_series = self.uow.series.get(series_id)

            if not found_series:
                raise NotFoundSeries()
            return SeriesDto.mapping(found_series)

    def remove_series(self, series_id: str):
        with self.uow:
            found_series = self.uow.series.get(series_id)
            if not found_series:
                raise NotFoundSeries()
            self.uow.series.delete(found_series)
            self.uow.commit()

    def update_series(self, update_dto: SeriesUpdateDto):
        with self.uow:
            found_series: Optional[Series] = self.uow.series.get(update_dto.id)
            if not found_series:
                raise NotFoundSeries()
            # post_id_list = list(map(lambda a: a.post_id, update_dto.series_post_list))
            # post_order_list = list(map(lambda a: a.order_number, update_dto.series_post_list))
            found_series.update(title=update_dto.title,
                                body=update_dto.body,
                                series_post_id_list=update_dto.series_post_list,
                                series_post_order_list=[i for i in range(len(update_dto.series_post_list))]
                                )
            self.uow.commit()

    def get_list(self, perPage: int, page: int) -> List[SeriesDto]:
        with self.uow:
            listing_series = self.uow.series \
                .get_series_dynamic_list(SeriesDynamicCondition(page=page, perPage=perPage))
            return [SeriesDto.mapping(s) for s in listing_series]

    def get_series_with_post(self, series_id: str) -> Optional[SeriesDto]:
        with self.uow:
            found_series = self.uow.series.get_series_with_post(series_id)
            if not found_series:
                raise NotFoundSeries()
            return SeriesDto.mapping_with_post(found_series)

    def get_series_by_post_id(self, post_id: str) -> List[SeriesDto]:
        with self.uow:
            series_list = self.uow.series.get_series_by_post_id(post_id=post_id)
            return [SeriesDto.mapping_with_post(s) for s in series_list]
