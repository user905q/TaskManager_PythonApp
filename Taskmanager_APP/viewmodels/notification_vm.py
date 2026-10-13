from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from models.repositories import TaskRepositoryExtended, NotificationsLogRepository


class NotificationViewModel(QObject):
    notificationShown = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.repo = TaskRepositoryExtended()
        self.log_repo = NotificationsLogRepository()
        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("TaskManager")
        menu = QMenu()
        action = QAction("Выход")
        action.triggered.connect(lambda: self.tray.hide())
        menu.addAction(action)
        self.tray.setContextMenu(menu)
        self.tray.show()
        self.timer = QTimer()
        self.timer.setInterval(60_000)
        self.timer.timeout.connect(self._check)
        self.timer.start()

    def _check(self):
        for task in self.repo.get_upcoming(minutes=5):
            self.tray.showMessage(
                "Приближается дедлайн!",
                f"Задача: {task.title}\nСрок: {task.deadline}",
                QSystemTrayIcon.MessageIcon.Warning, 5000)
            self.log_repo.log(task.id)
            self.notificationShown.emit(task.id)