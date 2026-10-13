from PyQt6.QtCore import QObject, pyqtSignal
from models.entities import Section
from models.repositories import SectionRepository


class SectionViewModel(QObject):
    sectionCreated = pyqtSignal(int)
    sectionDeleted = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo = SectionRepository()

    def create_section(self, name: str, color: str = "#4a90e2") -> int:
        section = Section(name=name, color=color)
        section_id = self.repo.create(section)
        self.sectionCreated.emit(section_id)
        return section_id

    def delete_with_tasks(self, section_id: int):
        self.repo.delete_with_tasks(section_id)
        self.sectionDeleted.emit()

    def delete_only(self, section_id: int):
        self.repo.delete_only(section_id)
        self.sectionDeleted.emit()

    def get_all(self):
        return self.repo.find_all()