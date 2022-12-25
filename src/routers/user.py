import logging
import pydantic
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.dependencies import get_transaction
from src.user.model import UserEntity
from pydantic import BaseModel
from src.infra.auth20 import Auth20

logger = logging.getLogger(__name__)
router = APIRouter(tags=["USER"])


class CreatedSuccessUser(pydantic.BaseModel):
    success: bool


class Auth20LoginReq(BaseModel):
    access_key: str
    platform: str


@router.get("/")
async def create_user(transaction: Session = Depends(get_transaction)):
    user = UserEntity("test", "1234", "bobo..")
    transaction.add(user)
    transaction.commit()
    return "hi"


@router.post("/auth20_login")
async def auth20_login(req: Auth20LoginReq):
    ret = Auth20.auth(req.platform, req.access_key)
    return ret
