from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    section_id: Optional[int] = None
    priority: str = "medium"
    status: str = "active"
    progress: int = 0
    deadline: Optional[str] = None
    color: str = "#ffffff"
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def validate(self):
        if not self.title or not self.title.strip():
            raise ValueError("Название задачи обязательно")


@dataclass
class Section:
    id: Optional[int] = None
    name: str = ""
    color: str = "#4a90e2"
    status: str = "active"
    created_at: Optional[str] = None

    def validate(self):
        if not self.name or not self.name.strip():
            raise ValueError("Название раздела обязательно")


@dataclass
class Tag:
    id: Optional[int] = None
    name: str = ""
    color: str = "#cccccc"


@dataclass
class BoardColumn:
    id: Optional[int] = None
    name: str = ""
    position: int = 0
    color: str = "#e0e0e0"


@dataclass
class Attachment:
    id: Optional[int] = None
    task_id: int = 0
    file_name: str = ""
    file_path: str = ""


@dataclass
class TimeLog:
    id: Optional[int] = None
    task_id: int = 0
    column_id: Optional[int] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    duration_sec: int = 0