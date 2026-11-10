from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import QTimer
from app.viewmodels.base import BaseViewModel
from app.models.notification_repo import NotificationRepo

class NotificationViewModel(BaseViewModel):
    # Сигнал для системного трея (покажет всплывающее окно)
    show_notification = pyqtSignal(str, str) # title, message

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.setInterval(60000) # Проверка раз в минуту
        self.timer.timeout.connect(self.check_deadlines)

    def start(self):
        self.timer.start()

    def check_deadlines(self):
        try:
            upcoming = NotificationRepo.get_upcoming_deadlines()
            for row in upcoming:
                msg = f"Дедлайн задачи: {row['title']} (до {row['deadline']})"
                self.show_notification.emit("Скоро дедлайн!", msg)
                NotificationRepo.log_notification(row['id'], 'deadline')
        except Exception as e:
            self.handle_exception(e)