from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from views.board_view import BoardView
from views.feed_view import FeedView
from views.stats_view import StatsView
from views.archive_view import ArchiveView
from views.dialogs.settings_dialog import SettingsDialog
from viewmodels.settings_vm import SettingsViewModel
from viewmodels.notification_vm import NotificationViewModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaskManager")
        self.resize(1200, 800)
        self.settings_vm = SettingsViewModel()
        self.notif_vm = NotificationViewModel()
        self.tabs = QTabWidget()
        self.tabs.addTab(BoardView(), "Главная")
        self.tabs.addTab(FeedView(), "Лента")
        self.tabs.addTab(StatsView(), "Статистика")
        self.tabs.addTab(ArchiveView(), "Архив")
        self.setCentralWidget(self.tabs)
        self._setup_menu()
        self._apply_theme(self.settings_vm.get_theme())

    def _setup_menu(self):
        menu = self.menuBar().addMenu("Настройки")
        menu.addAction("Тема оформления", self._open_settings)
        menu.addAction("О программе", self._about)

    def _open_settings(self):
        if SettingsDialog(self).exec():
            self._apply_theme(self.settings_vm.get_theme())

    def _about(self):
        QMessageBox.information(self, "О программе",
            "TaskManager v1.0\n\nДанные: tasks.db\nВложения: storage/")

    def _apply_theme(self, theme: str):
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; }
                QTabBar::tab { background: #2c2c2c; color: #e0e0e0; padding: 8px 16px; }
                QTabBar::tab:selected { background: #4a90e2; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #f5f5f5; color: #2c3e50; }
                QTabBar::tab { background: #ffffff; padding: 8px 16px; }
                QTabBar::tab:selected { background: #4a90e2; color: white; }
            """)