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

        # Сохраняем ссылки на вкладки
        self.board_view = BoardView()
        self.feed_view = FeedView()
        self.stats_view = StatsView()
        self.archive_view = ArchiveView()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.board_view, "Главная")
        self.tabs.addTab(self.feed_view, "Лента")
        self.tabs.addTab(self.stats_view, "Статистика")
        self.tabs.addTab(self.archive_view, "Архив")
        self.setCentralWidget(self.tabs)

        # Обновление вкладок при переключении
        self.tabs.currentChanged.connect(self._on_tab_changed)

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
        QMessageBox.information(
            self, "О программе",
            "TaskManager v1.0\n\nДанные: tasks.db\nВложения: storage/"
        )

    def _on_tab_changed(self, index):
        """Обновить вкладку при переключении."""
        widget = self.tabs.widget(index)

        # Обновить данные в зависимости от типа вкладки
        if hasattr(widget, "vm"):
            vm = widget.vm

            if hasattr(vm, "load_board"):
                vm.load_board()

            if hasattr(vm, "load_feed"):
                vm.load_feed()

            if hasattr(vm, "load_archive"):
                vm.load_archive()

            if hasattr(vm, "load_stats"):
                # Для статистики — перезагрузить данные
                if hasattr(widget, "_load_all"):
                    widget._load_all()
                elif hasattr(widget, "_reload"):
                    widget._reload()

    def _apply_theme(self, theme: str):
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; }
                QTabWidget::pane { border: 1px solid #333; }
                QTabBar::tab { background: #2c2c2c; color: #e0e0e0; padding: 8px 16px; }
                QTabBar::tab:selected { background: #4a90e2; }
                QPushButton {
                    background: #4a90e2; color: white;
                    padding: 6px 12px; border-radius: 4px;
                }
                QLineEdit, QComboBox, QTextEdit, QDateTimeEdit {
                    background: #2c2c2c; color: #e0e0e0;
                    border: 1px solid #444; padding: 4px;
                }
                QLabel { color: #e0e0e0; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #f5f5f5; color: #2c3e50; }
                QTabWidget::pane { border: 1px solid #e0e0e0; }
                QTabBar::tab { background: #ffffff; padding: 8px 16px; }
                QTabBar::tab:selected { background: #4a90e2; color: white; }
                QPushButton {
                    background: #4a90e2; color: white;
                    padding: 6px 12px; border-radius: 4px;
                }
            """)