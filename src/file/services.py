import uuid
import pydantic
import fastapi
import os
from pathlib import Path

from src.unit_of_work import SqlAlchemyUow
from src.file.repositories import FileRepository
from src.file.models import FileModel, FileStatus


class NotFoundFileModel(Exception):
    def __init__(self):
        self.message = "존재 하지 않는 파일"


class FileModelDto(pydantic.BaseModel):
    dir: str
    ext: str
    file_id: str

    def get_path(self) -> str:
        return f"{self.dir}/{self.file_id}.{self.ext}"


class FileService:
    def __init__(self, uow: SqlAlchemyUow, static_file_root_path: str = "./static"):
        self.uow = uow
        self.static_file_root_path = static_file_root_path

    async def save_file(self, user_id, file: fastapi.UploadFile) -> str:
        file_id = uuid.uuid4().hex
        ext = file.filename.split('.')[1]
        content_type = file.content_type
        origin_filename = file.filename
        save_dir = self.static_file_root_path + f"/{user_id}"
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        save_dir = save_dir + f"/{file_id}.{ext}"
        await FileRepository.save_file(file, save_dir)
        with self.uow:
            self.uow.files.add(FileModel(
                id=file_id,
                status=FileStatus.normal,
                dir=self.static_file_root_path + f"/{user_id}",
                content_type=content_type,
                ext=ext,
                origin_name=origin_filename,
                size=os.path.getsize(save_dir)
            ))
            self.uow.commit()
        return file_id

    async def load_file_model(self, file_id: str) -> FileModelDto:
        with self.uow:
            file = self.uow.files.get(file_id)
            if not file:
                raise NotFoundFileModel()
            return FileModelDto(dir=file.dir, file_id=file.id, ext=file.ext)
