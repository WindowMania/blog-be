import uuid
import pydantic
import fastapi
from pathlib import Path

from src.unit_of_work import SqlAlchemyUow
from src.file.repositories import FileRepository, FileModelRepository


class FileService:
    def __init__(self, uow: SqlAlchemyUow):
        self.uow = uow
        self.home_dir = "~/blog/static"

    async def save_file(self, user_id, file: fastapi.File) -> str:
        file_id = uuid.uuid4().hex
        ext = file.filename.split('.')[1]
        save_dir = self.home_dir + f"/{user_id}"
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        await FileRepository.save_file(file, save_dir + f"/{file_id}.{ext}")
        return file_id
