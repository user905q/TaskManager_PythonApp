from app.viewmodels.base import BaseViewModel
from app.models.section_repo import SectionRepo
from app.models.entities import Section

class SectionViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()

    def create_section(self, name: str, color: str):
        try:
            section = Section(name=name, color=color)
            SectionRepo.create(section)
            self.data_changed.emit("sections")
        except Exception as e:
            self.handle_exception(e)

    def update_section(self, section_id: int, name: str, color: str):
        try:
            SectionRepo.update(section_id, name, color)
            self.data_changed.emit("sections")
            self.data_changed.emit("tasks")
        except Exception as e:
            self.handle_exception(e)

    def delete_section(self, section_id: int, delete_tasks: bool = False):
        try:
            if delete_tasks:
                SectionRepo.delete_with_tasks(section_id)
            else:
                SectionRepo.delete_section_only(section_id)
            self.data_changed.emit("sections")
            self.data_changed.emit("tasks")
        except Exception as e:
            self.handle_exception(e)

    def archive_section(self, section_id: int):
        try:
            SectionRepo.archive_section(section_id)
            self.data_changed.emit("sections")
            self.data_changed.emit("tasks")
            self.data_changed.emit("archive")
        except Exception as e:
            self.handle_exception(e)