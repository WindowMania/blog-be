import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Union

from src.user.unit_of_work import UserUnitOfWork
from src.dependencies import get_user_uow, get_jwt_ctx, JwtContext, get_current_user
from src.user.model import UserEntity
import src.user.service as user_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["USER"])


class Auth20LoginReq(BaseModel):
    access_key: str
    platform: str


class HomepageLoginReq(BaseModel):
    account: str
    password: str


class Token(BaseModel):
    access_key: str


class UserRes(BaseModel):
    account: str


@router.post("/oauth_login", response_model=Token)
async def oauth_login(req: Auth20LoginReq,
                      user_uow: UserUnitOfWork = Depends(get_user_uow),
                      jwt_ctx: JwtContext = Depends(get_jwt_ctx)
                      ):
    access_key = user_service.login_oauth20(user_uow, jwt_ctx, req.platform, req.access_key)
    return Token(access_key=access_key)


@router.post("/login", response_model=Token)
async def login(req: Union[HomepageLoginReq, Auth20LoginReq],
                user_uow: UserUnitOfWork = Depends(get_user_uow),
                jwt_ctx: JwtContext = Depends(get_jwt_ctx)
                ):
    access_key = None
    if isinstance(req, Auth20LoginReq):
        access_key = user_service.login_oauth20(user_uow, jwt_ctx, req.platform, req.access_key)
    return Token(access_key=access_key)


@router.get("/me", response_model=UserRes)
async def get_current_user(current_user: UserEntity = Depends(get_current_user)):
    return UserRes(account=current_user.account)
