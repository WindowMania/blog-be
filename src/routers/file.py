import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
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
    try:
        fileId = await file_service.save_file(user.id, file)
        return FileUploadRes(fileId=fileId)
    except Exception as e:
        raise HTTPException(500, detail=e.message)


@router.get("/static/{file_id}")
async def get_file(
        file_id: str,
        file_service=Depends(get_file_service)
):
    try:
        file_model_dto = await file_service.load_file_model(file_id)
        return FileResponse(path=file_model_dto.get_path())
    except Exception as e:
        raise HTTPException(500, detail=e.message)
