import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List

from src.dependencies import get_post_service, get_current_user, get_series_service
from src.post.services import PostService, SeriesService, PostDto, PostUpdateDto, PostDynamicCondition, TagStatistics, \
    SeriesDto, SeriesUpdateDto
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


class SeriesCreateReq(BaseModel):
    title: str
    body: str
    post_id_list: List[str]


class PostCreateRes(BaseModel):
    id: str


class SeriesCreateRes(BaseModel):
    id: str


class PostDeleteReq(BaseModel):
    id: str
    deleted: bool


class TagReq(BaseModel):
    tag: str


class TagStatisticsRes(BaseModel):
    tags: List[TagStatistics]


class SeriesListRes(BaseModel):
    page: int
    perPage: int
    seriesList: List[SeriesDto]


class SeriesRes(BaseModel):
    series: SeriesDto


class SeriesUpdate(BaseModel):
    id: str
    title: str
    body: str
    postIdList: List[str]


class SeriesListByPostId(BaseModel):
    seriesList: List[SeriesDto]


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


@router.post('/series', response_model=SeriesCreateRes)
async def create_series(req: SeriesCreateReq,
                        series_service: SeriesService = Depends(get_series_service),
                        user: UserEntity = Depends(get_current_user)
                        ):
    try:
        series_id = series_service.create_series(user_id=user.id, title=req.title, body=req.body,
                                                 post_id_list=req.post_id_list)
        return SeriesCreateRes(id=series_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/series-with-post", response_model=SeriesRes)
async def get_series_with_post(seriesId: str = Query(""),
                               series_service: SeriesService = Depends(get_series_service)
                               ):
    try:
        ret = series_service.get_series_with_post(series_id=seriesId)
        return SeriesRes(series=ret)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get('/series', response_model=SeriesRes)
async def get_series(seriesId: str = Query(""),
                     series_service: SeriesService = Depends(get_series_service)
                     ):
    try:
        ret = series_service.find_series(series_id=seriesId)
        return SeriesRes(series=ret)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/series")
async def delete_series(seriesId: str = Query(""),
                        series_service: SeriesService = Depends(get_series_service),
                        user: UserEntity = Depends(get_current_user)
                        ):
    try:
        series_service.remove_series(series_id=seriesId)
        return 'ok'
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/series")
async def update_series(req: SeriesUpdate,
                        series_service: SeriesService = Depends(get_series_service),
                        user: UserEntity = Depends(get_current_user)
                        ):
    try:
        series_service.update_series(
            SeriesUpdateDto(
                id=req.id,
                title=req.title,
                body=req.body,
                series_post_list=req.postIdList
            )
        )
        return 'ok'
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/series/list", response_model=SeriesListRes)
async def get_series_list(page: int = Query(1),
                          perPage: int = Query(10),
                          series_service: SeriesService = Depends(get_series_service)
                          ):
    try:
        ret = series_service.get_list(page=page, perPage=perPage)
        return SeriesListRes(page=page, perPage=perPage, seriesList=ret)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/series/post-id/{post_id}", response_model=SeriesListByPostId)
async def get_series_by_post_id(
        post_id: str,
        series_service: SeriesService = Depends(get_series_service)
):
    try:
        series_list = series_service.get_series_by_post_id(post_id=post_id)
        return SeriesListByPostId(seriesList=series_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put('')
async def update_post(req: PostUpdateReq,
                      post_service: PostService = Depends(get_post_service),
                      user: UserEntity = Depends(get_current_user)):
    try:
        # ????????? ????????? ?????? ????????? ?????? ??? ??? ????????? ?????? ?????? ????????????.
        # ????????? ?????? ?????????.
        post_update_dto: PostUpdateDto = PostUpdateDto(id=req.id, title=req.title, body=req.body, tags=req.tags)
        post_service.update_post(post_update_dto)
        return 'ok'
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get('/list', response_model=PostListRes)
async def get_list(page: int = Query(1),
                   perPage: int = Query(10),
                   tags: list[str] = Query(["All"]),
                   title: str = Query(None),
                   post_service: PostService = Depends(get_post_service)
                   ):
    try:
        cond = PostDynamicCondition(page=page, perPage=perPage, deleted=False, tags=tags,
                                    title=title
                                    )
        posts = post_service.get_post_dynamic_list(cond)
        return PostListRes(page=page, perPage=perPage, posts=posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{post_id}", response_model=PostDto)
async def get_post(post_id: str, post_service: PostService = Depends(get_post_service)):
    try:
        if not post_id or post_id == 'undefined':
            exp = Exception()
            exp.message = "????????? ?????????"
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
#         print("????????",user,user.id)
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
