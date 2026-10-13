from PyQt6.QtCore import QObject, pyqtSignal
from models.repositories import SettingsRepository


class SettingsViewModel(QObject):
    themeChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.repo = SettingsRepository()

    def get_theme(self) -> str:
        return self.repo.get("theme", "light")

    def set_theme(self, theme: str):
        self.repo.set("theme", theme)
        self.themeChanged.emit(theme)