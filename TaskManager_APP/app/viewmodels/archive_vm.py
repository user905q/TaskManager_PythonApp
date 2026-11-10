from app.viewmodels.base import BaseViewModel
from app.models.archive_repo import ArchiveRepo

class ArchiveViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()

    def get_archive_data(self):
        try:
            sections = ArchiveRepo.get_archived_sections()
            tasks = ArchiveRepo.get_archived_tasks()
            return sections, tasks
        except Exception as e:
            self.handle_exception(e)
            return [], []

    def restore_task(self, task_id: int):
        try:
            ArchiveRepo.restore_task(task_id)
            self.data_changed.emit("archive")
            self.data_changed.emit("tasks") 
        except Exception as e:
            self.handle_exception(e)

    def restore_section(self, section_id: int):
        try:
            ArchiveRepo.restore_section(section_id)
            self.data_changed.emit("archive")
            self.data_changed.emit("sections")
            self.data_changed.emit("tasks")
        except Exception as e:
            self.handle_exception(e)