import uuid
from datetime import datetime
from typing import List

from src.user.models import UserEntity


class Tag:
    id: str
    created_at: datetime
    updated_at: datetime

    def __init__(self, tag: str):
        self.id = tag


class PostTag:
    id: str
    post_id: str
    tag_id: str
    created_at: datetime
    updated_at: datetime
    tag: Tag

    def __init__(self, post_id: str, tag_id: str):
        self.id = uuid.uuid4().hex
        self.post_id = post_id
        self.tag_id = tag_id


class Post:
    id: str
    user_id: str
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
    deleted: bool

    user: UserEntity
    post_tags: List[PostTag]

    def __init__(self, user_id: str, title: str, body: str, tags: List[str]):
        self.id = uuid.uuid4().hex
        self.user_id = user_id
        self.title = title
        self.body = body
        self.deleted = False
        self.post_tags = [PostTag(self.id, tag) for tag in tags]
