import uuid
import pydantic
import fastapi
import os
from pathlib import Path

from src.unit_of_work import SqlAlchemyUow
from src.file.repositories import FileRepository, FileModelRepository
from src.file.models import FileModel, FileStatus


class FileService:
    def __init__(self, uow: SqlAlchemyUow):
        self.uow = uow
        self.home_dir = "~/blog/static"

    async def save_file(self, user_id, file: fastapi.UploadFile) -> str:
        file_id = uuid.uuid4().hex
        ext = file.filename.split('.')[1]
        content_type = file.content_type
        origin_filename = file.filename
        save_dir = self.home_dir + f"/{user_id}"
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        save_dir = save_dir + f"/{file_id}.{ext}"
        await FileRepository.save_file(file, save_dir)
        with self.uow:
            self.uow.files.add(FileModel(
                id=file_id,
                status=FileStatus.normal,
                content_type=content_type,
                ext=ext,
                origin_name=origin_filename,
                size=os.path.getsize(save_dir)
            ))
            self.uow.commit()
        return file_id
