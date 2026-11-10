from app.viewmodels.base import BaseViewModel
from app.models.settings_repo import SettingsRepo

class SettingsViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()

    def get_theme(self) -> str:
        try:
            return SettingsRepo.get("theme", "light")
        except Exception as e:
            self.handle_exception(e)
            return "light"

    def set_theme(self, theme_name: str):
        try:
            SettingsRepo.set("theme", theme_name)
            self.data_changed.emit("theme")
        except Exception as e:
            self.handle_exception(e)