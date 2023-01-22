import aiofiles
import fastapi

from typing import Optional
from sqlalchemy.orm import Session, joinedload

from src.infra.repository import SqlAlchemyRepository
from src.file.models import FileModel


class FileRepository:

    @staticmethod
    async def save_file(f: fastapi.File, directory: str):
        async with aiofiles.open(directory, 'wb') as out_file:
            while content := await f.read(1024):  # async read chunk
                await out_file.write(content)  # async write chunk


    @staticmethod
    async def load_file(directory: str):
        async with aiofiles.open(directory, 'r') as read_file:
            contents = await read_file.read()
        return contents


class FileModelRepository(SqlAlchemyRepository):
    def __init__(self, session: Session):
        super().__init__(session, FileModel)

    def get(self, ref) -> Optional[FileModel]:
        return super().get(ref)
