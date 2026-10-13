from PyQt6.QtCore import QObject, pyqtSignal
from models.repositories import TaskRepository, SectionRepository


class ArchiveViewModel(QObject):
    archiveLoaded = pyqtSignal(list, list)

    def __init__(self):
        super().__init__()
        self.task_repo = TaskRepository()
        self.sec_repo = SectionRepository()
        self.db = self.task_repo.db

    def load_archive(self):
        tasks = self.task_repo.find_archived()
        cur = self.db.cursor()
        sections = cur.execute(
            "SELECT * FROM sections WHERE status='archived'"
        ).fetchall()
        self.archiveLoaded.emit(tasks, [dict(s) for s in sections])
        return tasks

    def restore_task(self, task_id: int):
        self.task_repo.restore(task_id)

    def restore_section(self, section_id: int):
        self.sec_repo.restore(section_id)