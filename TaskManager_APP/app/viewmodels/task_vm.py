from app.viewmodels.base import BaseViewModel
from app.models.task_repo import TaskRepo
from app.models.tag_repo import TagRepo
from app.models.entities import Task

class TaskViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()

    def create_task(self, title: str, description: str, section_id: int = None):
        try:
            task = Task(title=title, description=description, section_id=section_id)
            TaskRepo.create(task)
            self.data_changed.emit("tasks")  # Говорим интерфейсу: "Обнови задачи!"
        except Exception as e:
            self.handle_exception(e)

    def archive_task(self, task_id: int):
        try:
            TaskRepo.archive(task_id)
            self.data_changed.emit("tasks")
            self.data_changed.emit("archive")
        except Exception as e:
            self.handle_exception(e)

    def delete_task(self, task_id: int):
        try:
            TaskRepo.delete(task_id)
            self.data_changed.emit("tasks")
        except Exception as e:
            self.handle_exception(e)

    def add_tag_to_task(self, task_id: int, tag_name: str):
        try:
            tags = TagRepo.get_all()
            tag_id = next((t.id for t in tags if t.name == tag_name), None)
            if not tag_id:
                tag_id = TagRepo.create(tag_name)
            TagRepo.add_to_task(task_id, tag_id)
            self.data_changed.emit("tasks")
        except Exception as e:
            self.handle_exception(e)

    def get_tags_for_task(self, task_id: int):
        try:
            return TagRepo.get_for_task(task_id)
        except Exception as e:
            self.handle_exception(e)
            return []

    def get_all_tags(self):
        try:
            return TagRepo.get_all()
        except Exception as e:
            self.handle_exception(e)
            return []

    def add_attachment(self, task_id: int, filepath: str):
        try:
            from app.models.attachment_repo import AttachmentRepo
            AttachmentRepo.add_attachment(task_id, filepath)
            self.data_changed.emit("tasks")
        except Exception as e:
            self.handle_exception(e)

    def update_task(self, task_id: int, title: str, description: str, section_id: int, deadline):
        try:
            TaskRepo.update(task_id, title, description, section_id, deadline)
            self.data_changed.emit("tasks")
        except Exception as e:
            self.handle_exception(e)

    def remove_tag_from_task(self, task_id: int, tag_id: int):
        try:
            TagRepo.remove_from_task(task_id, tag_id)
            self.data_changed.emit("tasks")
        except Exception as e:
            self.handle_exception(e)