import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List

from src.dependencies import get_post_service, get_current_user, get_post_test_service
from src.post.services import PostService, PostDto, PostUpdateDto, PostDynamicCondition, TagStatistics
from src.user.models import UserEntity

logger = logging.getLogger(__name__)
router = APIRouter(tags=["POST"])


class PostCreateReq(BaseModel):
    title: str
    body: str
    tags: List[str]


class PostListReq(BaseModel):
    page: int
    perPage: int


class PostListRes(BaseModel):
    page: int
    perPage: int
    posts: List[PostDto]


class PostUpdateReq(BaseModel):
    id: str
    title: str
    body: str
    tags: List[str]


class PostCreateRes(BaseModel):
    id: str


class PostDeleteReq(BaseModel):
    id: str
    deleted: bool


class TagReq(BaseModel):
    tag: str


class TagStatisticsRes(BaseModel):
    tags: List[TagStatistics]


@router.post('', response_model=PostCreateRes)
async def create_post(req: PostCreateReq,
                      post_service: PostService = Depends(get_post_service),
                      user: UserEntity = Depends(get_current_user)
                      ):
    try:
        post_id = post_service.create_post(user.id, req.title, req.body, req.tags)
        return PostCreateRes(id=post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put('')
async def update_post(req: PostUpdateReq,
                      post_service: PostService = Depends(get_post_service),
                      user: UserEntity = Depends(get_current_user)):
    try:
        # 로그인 유저가 해당 게시글 수정 할 수 있는지 권한 체크 넣어야함.
        # 지금은 일단 빼놨다.
        post_update_dto: PostUpdateDto = PostUpdateDto(id=req.id, title=req.title, body=req.body, tags=req.tags)
        post_service.update_post(post_update_dto)
        return 'ok'
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get('/list', response_model=PostListRes)
async def get_list(page: int = Query(1),
                   perPage: int = Query(10),
                   tags: list[str] = Query(["All"]),
                   post_service: PostService = Depends(get_post_service)
                   ):
    try:
        cond = PostDynamicCondition(page=page, perPage=perPage, deleted=False, tags=tags)
        posts = post_service.get_post_dynamic_list(cond)
        return PostListRes(page=page, perPage=perPage, posts=posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{post_id}", response_model=PostDto)
async def get_post(post_id: str, post_service: PostService = Depends(get_post_service)):
    try:
        if not post_id or post_id == 'undefined':
            exp = Exception()
            exp.message = "잘못된 아이디"
            raise exp
        return post_service.get_post(post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put('/set-delete')
async def delete_post(req: PostDeleteReq,
                      post_service: PostService = Depends(get_post_service),
                      user: UserEntity = Depends(get_current_user)):
    try:
        post_service.set_delete_post(req.id, req.deleted)
        return 'ok'
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


# @router.post("/test/dummy")
# async def create_dummy_post(post_test_service=Depends(get_post_test_service),
#                             user: UserEntity = Depends(get_current_user)):
#     try:
#         print("뭐가??",user,user.id)
#         post_test_service.create_dummy_posts(user.id)
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500)


@router.post('/tag')
async def create_tag(
        req: TagReq,
        post_service=Depends(get_post_service),
        user: UserEntity = Depends(get_current_user)
):
    try:
        post_service.upsert_tag(req.tag)
        return 'ok'
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


@router.delete("/tag")
async def delete_tag(name: str,
                     post_service=Depends(get_post_service),
                     user: UserEntity = Depends(get_current_user)
                     ):
    try:
        post_service.delete_tag(name)
        return 'ok'
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


@router.get("/tag/statistics", response_model=TagStatisticsRes)
async def get_tag_statistics(post_service=Depends(get_post_service)):
    try:
        tags = post_service.get_tag_statistics()
        return TagStatisticsRes(tags=tags)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)
