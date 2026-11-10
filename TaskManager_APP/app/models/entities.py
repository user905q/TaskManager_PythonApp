from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class ValidationError(Exception):
    pass

@dataclass
class Section:
    id: Optional[int] = None
    name: str = ""
    color: str = "#6B7280"
    is_system: bool = False
    is_archived: bool = False
    created_at: Optional[datetime] = None

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    section_id: Optional[int] = None
    color: str = "#FFFFFF"
    deadline: Optional[datetime] = None
    is_archived: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Tag:
    id: Optional[int] = None
    name: str = ""

@dataclass
class BoardColumn:
    id: Optional[int] = None
    name: str = ""
    position: int = 0

@dataclass
class Attachment:
    id: Optional[int] = None
    task_id: Optional[int] = None
    original_name: str = ""
    stored_name: str = ""
    size: int = 0
    added_at: Optional[datetime] = None

@dataclass
class TimeLog:
    id: Optional[int] = None
    task_id: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_sec: Optional[int] = None