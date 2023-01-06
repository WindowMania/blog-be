from datetime import datetime
from src.user.models import UserEntity


class Tag:
    id: str
    created_at: datetime
    updated_at: datetime


class Post:
    id: str
    user_id: str
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
    deleted: bool

    user: UserEntity


class PostTag:
    id: str
    post_id: str
    tag_id: str
    created_at: datetime
    updated_at: datetime

    tag: Tag
    post: Post
