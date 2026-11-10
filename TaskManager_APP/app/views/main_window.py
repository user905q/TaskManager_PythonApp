from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from app.viewmodels.notification_vm import NotificationViewModel
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QToolBar, QLabel
from PyQt6.QtGui import QAction
from app.views.dialogs.about_dialog import AboutDialog
from app.views.dialogs.task_dialog import TaskDialog
from app.views.dialogs.section_dialog import SectionDialog
from app.views.board_tab import BoardTab
from app.views.feed_tab import FeedTab
from app.views.stats_tab import StatsTab
from app.views.archive_tab import ArchiveTab
from app.views.dialogs.columns_dialog import ColumnsDialog
from app.viewmodels.settings_vm import SettingsViewModel
from app.config import BASE_DIR

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(1200, 800)

        self.settings_vm = SettingsViewModel()
        
        # 1. Центральный виджет - вкладки
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Инициализируем вкладки
        self.board_tab = BoardTab()
        self.feed_tab = FeedTab()
        self.stats_tab = StatsTab()
        self.archive_tab = ArchiveTab()

        self.tabs.addTab(self.board_tab, "Главная")
        self.tabs.addTab(self.feed_tab, "Лента")
        self.tabs.addTab(self.stats_tab, "Статистика")
        self.tabs.addTab(self.archive_tab, "Архив")

        # Обновление вкладок при переключении
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # 2. Тулбар
        self.toolbar = QToolBar("Главная панель")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.action_new_task = QAction("+ Новая задача", self)
        self.action_new_task.triggered.connect(self.open_task_dialog)
        self.toolbar.addAction(self.action_new_task)

        self.action_new_section = QAction("+ Новый раздел", self)
        self.action_new_section.triggered.connect(self.open_section_dialog)
        self.toolbar.addAction(self.action_new_section)

        self.action_columns = QAction("Колонки", self)
        self.action_columns.triggered.connect(self.open_columns_dialog)
        self.toolbar.addAction(self.action_columns)

        self.action_theme = QAction("Сменить тему", self)
        self.action_theme.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(self.action_theme)

        # 3. Меню
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

                # Настройка системного трея и уведомлений
        self.tray_icon = QSystemTrayIcon(self)
        # Создаем простую иконку (или используй свою картинку, если есть)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation))
        self.tray_icon.setToolTip("Task Manager")
        self.tray_icon.show()

        # Контекстное меню для трея (чтобы можно было закрыть программу)
        tray_menu = QMenu()
        action_quit = QAction("Выход", self)
        action_quit.triggered.connect(self.close) # Закрывает окно
        tray_menu.addAction(action_quit)
        self.tray_icon.setContextMenu(tray_menu)

        # Запуск таймера уведомлений
        self.notif_vm = NotificationViewModel()
        self.notif_vm.show_notification.connect(self.show_tray_notification)
        self.notif_vm.start()

        # Применяем сохраненную тему при запуске
        self.apply_theme(self.settings_vm.get_theme())

    def show_tray_notification(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)



    def on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        if hasattr(widget, 'load_tasks'):
            widget.load_tasks()
        elif hasattr(widget, 'load_data'):
            widget.load_data()
        elif hasattr(widget, 'refresh_data'):
            widget.refresh_data()

    def open_task_dialog(self):
        dialog = TaskDialog(self)
        if dialog.exec():
            self.board_tab.refresh_data()
            self.feed_tab.load_tasks()

    def open_section_dialog(self):
        dialog = SectionDialog(self)
        if dialog.exec():
            self.board_tab.refresh_data()
            self.feed_tab.load_tasks()

    def toggle_theme(self):
        current = self.settings_vm.get_theme()
        new_theme = "light" if current == "dark" else "dark"
        self.settings_vm.set_theme(new_theme)
        self.apply_theme(new_theme)

        if hasattr(self, 'stats_tab'):
            self.stats_tab.load_data()

    def apply_theme(self, theme_name):
        theme_path = BASE_DIR / "app" / "resources" / "styles" / f"{theme_name}.qss"
        if theme_path.exists():
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def open_columns_dialog(self):
        dialog = ColumnsDialog(self)
        if dialog.exec():
            self.board_tab.refresh_data()
            self.feed_tab.load_tasks()
            self.stats_tab.load_data() 