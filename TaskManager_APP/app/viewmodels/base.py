from PyQt6.QtCore import QObject, pyqtSignal
from app.db.connection import DBError
from app.models.entities import ValidationError

class BaseViewModel(QObject):
    # Сигналы для связи с View
    error_occurred = pyqtSignal(str)      # Для показа ошибок пользователю
    data_changed = pyqtSignal(str)        # Для обновления интерфейса (передается тип: 'tasks', 'sections' и т.д.)

    def handle_exception(self, e: Exception):
        """Централизованная обработка ошибок: пишем в лог/шлет сигнал в UI"""
        if isinstance(e, (ValidationError, DBError)):
            self.error_occurred.emit(str(e))
        else:
            self.error_occurred.emit(f"Непредвиденная ошибка: {e}")