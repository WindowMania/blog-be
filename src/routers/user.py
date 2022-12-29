import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Union

from src.user.unit_of_work import SqlAlchemyUow
from src.dependencies import get_user_auth_service, get_current_user
from src.infra.oauth import OAuthPlatform
from src.user.service import UserAuthService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["USER"])


class OAuthReq(BaseModel):
    code: str
    platform: OAuthPlatform


class OAuthRes(BaseModel):
    access_key: str


class LoginReq(BaseModel):
    account: str
    password: str


# class Token(BaseModel):
#     access_key: str
#
#
# class UserRes(BaseModel):
#     account: str
#

# @router.post("/reauthorize", response_model=Token)
# async def oauth_login(req: Auth20LoginReq,
#                       user_auth_service: UserAuthService = Depends(get_user_auth_service)
#
#                       ):
#     user_auth_service.reauthorize_by_oauth(req.)
#
#     access_key = user_service.reauthorize(user_uow, jwt_ctx, req.platform, req.access_key)
#     return Token(access_key=access_key)

# @router.get("/me", response_model=UserRes)
# async def get_current_user(current_user: UserEntity = Depends(get_current_user)):
#     return UserRes(account=current_user.account)


@router.post("/oauth", response_model=OAuthRes)
async def oauth_get_access_key(
        req: OAuthReq,
        user_auth_service: UserAuthService = Depends(get_user_auth_service)

):
    access_key = user_auth_service.reauthorize_by_oauth(req.code, req.platform)
    return OAuthRes(access_key=access_key)
