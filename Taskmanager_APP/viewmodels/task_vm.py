from PyQt6.QtCore import QObject, pyqtSignal
from models.entities import Task
from models.repositories import TaskRepository, TagRepository, AttachmentRepository


class TaskViewModel(QObject):
    taskCreated = pyqtSignal(int)
    taskUpdated = pyqtSignal(int)
    taskDeleted = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.repo = TaskRepository()
        self.tag_repo = TagRepository()
        self.attach_repo = AttachmentRepository()

    def create_task(self, data: dict) -> int:
        task = Task(**data)
        task_id = self.repo.create(task)
        self.taskCreated.emit(task_id)
        return task_id

    def update_task(self, task_id: int, data: dict):
        task = self.repo.find_by_id(task_id)
        for key, value in data.items():
            setattr(task, key, value)
        self.repo.update(task)
        self.taskUpdated.emit(task_id)

    def delete_task(self, task_id: int):
        self.repo.delete(task_id)
        self.taskDeleted.emit(task_id)

    def archive_task(self, task_id: int):
        self.repo.archive(task_id)

    def get_all_tags(self):
        return self.tag_repo.find_all()

    def get_task_tags(self, task_id: int):
        return self.tag_repo.get_task_tags(task_id)

    def get_attachments(self, task_id: int):
        return self.attach_repo.find_by_task(task_id)