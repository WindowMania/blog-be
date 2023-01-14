import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

from src.dependencies import get_post_service, get_current_user
from src.post.services import PostService, PostDto
from src.user.models import UserEntity

logger = logging.getLogger(__name__)
router = APIRouter(tags=["POST"])


class PostCreateReq(BaseModel):
    title: str
    content: str
    tags: List[str]


class PostCreateRes(BaseModel):
    post_id: str


@router.post('', response_model=PostCreateRes)
async def create_post(req: PostCreateReq,
                      post_service: PostService = Depends(get_post_service),
                      user: UserEntity = Depends(get_current_user)
                      ):
    try:
        # 밑 태그 추가 하는 API 만들어야 한다..
        post_service.upsert_tag("All")
        post_id = post_service.create_post(user.id, req.title, req.content, req.tags)
        return PostCreateRes(post_id=post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{post_id}", response_model=PostDto)
async def get_post(post_id: str, post_service: PostService = Depends(get_post_service)):
    try:
        return post_service.get_post(post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)
