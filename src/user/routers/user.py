import logging
import pydantic
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from src.dependencies import get_transaction
from src.user.aggregate.user import User
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["USER"])


class CreatedSuccessUser(pydantic.BaseModel):
    success: bool


class Auth20LoginReq(BaseModel):
    access_key: str
    platform: str


@router.get("/")
async def create_user(transaction: Session = Depends(get_transaction)):
    user = User("test", "1234", "bobo..")
    transaction.add(user)
    transaction.commit()
    return "hi"


@router.post("/auth20_login")
async def auth20_login(req: Auth20LoginReq):
    return req
