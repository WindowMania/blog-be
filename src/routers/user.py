import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Union

from src.user.unit_of_work import SqlAlchemyUow
from src.dependencies import get_user_auth_service, get_user_service, get_user_email_service
from src.infra.oauth import OAuthPlatform
from src.user.services import UserAuthService, UserEmailService, UserService

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


class JoinReq(BaseModel):
    email: str
    password: str
    nick_name: str


class JoinAuthCodeReq(BaseModel):
    account: str
    code: str


@router.post("/join")
async def join(req: JoinReq,
               user_service: UserService = Depends(get_user_service),
               user_email_service: UserEmailService = Depends(get_user_email_service)
               ):
    try:
        user_service.create_user(req.email, req.password, req.nick_name)
        user_email_service.send_join_verify_email(req.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/join/verify")
async def join(req: JoinAuthCodeReq,
               user_service: UserService = Depends(get_user_service)
               ):
    try:
        user_service.join_verify(account=req.account, code=req.code)
        return "ok"
    except Exception as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/oauth", response_model=OAuthRes)
async def oauth_get_access_key(
        req: OAuthReq,
        user_auth_service: UserAuthService = Depends(get_user_auth_service)

):
    access_key = user_auth_service.reauthorize_by_oauth(req.code, req.platform)
    return OAuthRes(access_key=access_key)
