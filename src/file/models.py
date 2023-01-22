from enum import Enum
from typing import Optional
from datetime import datetime


class FileStatus(str, Enum):
    normal = "normal"
    deleted = "deleted"


class FileModel:
    id: str
    status: FileStatus
    dir: str
    content_type: str
    ext: str
    origin_name: str
    size: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __init__(self, id: str,
                 dir: str,
                 status: FileStatus,
                 content_type: str,
                 ext: str,
                 origin_name: str,
                 size: int
                 ):
        self.id = id
        self.status = status
        self.dir = dir
        self.content_type = content_type
        self.ext = ext
        self.origin_name = origin_name
        self.size = size
        self.created_at = None
        self.updated_at = None
