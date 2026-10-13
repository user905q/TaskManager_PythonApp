from PyQt6.QtCore import QObject, pyqtSignal
from models.repositories import TaskRepositoryExtended, SectionRepository, TagRepository


class FeedViewModel(QObject):
    feedLoaded = pyqtSignal(list)
    filterApplied = pyqtSignal(list)
    emptyResult = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo = TaskRepositoryExtended()
        self.sec_repo = SectionRepository()
        self.tag_repo = TagRepository()

    def load_feed(self):
        tasks = self.repo.find_all()
        self.feedLoaded.emit(tasks)
        return tasks

    def get_sections(self):
        return self.sec_repo.find_all()

    def get_tags(self):
        return self.tag_repo.find_all()

    def apply_filter(self, criteria: dict):
        tasks = self.repo.find_by_filter(criteria)
        if not tasks:
            self.emptyResult.emit()
        else:
            self.filterApplied.emit(tasks)
        return tasks