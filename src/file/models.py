from enum import Enum
from typing import Optional
from datetime import datetime


class FileStatus(str, Enum):
    normal = "normal"
    deleted = "deleted"


class FileModel:
    id: str
    status: FileStatus
    content_type: str
    ext: str
    origin_name: str
    size: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
