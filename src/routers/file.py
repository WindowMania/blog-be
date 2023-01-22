import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel

from src.dependencies import get_current_user, get_file_service
from src.user.models import UserEntity

logger = logging.getLogger(__name__)
router = APIRouter(tags=["File"])


class FileUploadRes(BaseModel):
    fileId: str


@router.post('', response_model=FileUploadRes)
async def create_file(
        file: UploadFile,
        file_service=Depends(get_file_service),
        user: UserEntity = Depends(get_current_user)
):
    fileId = await file_service.save_file(user.id, file)
    print("뭐지?", fileId)
    return FileUploadRes(fileId=fileId)
