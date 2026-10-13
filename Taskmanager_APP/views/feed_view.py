from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from viewmodels.feed_vm import FeedViewModel
from models.repositories import TaskRepositoryExtended


class FeedView(QWidget):
    def __init__(self):
        super().__init__()
        self.vm = FeedViewModel()
        self.task_repo = TaskRepositoryExtended()

        # Подключаем сигналы
        self.vm.feedLoaded.connect(self._on_loaded)
        self.vm.filterApplied.connect(self._on_loaded)
        self.vm.emptyResult.connect(lambda: self._on_loaded([]))

        self._build_ui()
        self._load_filters()

        # Загрузить все задачи при инициализации
        self._load_all()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Поиск
        search = QHBoxLayout()
        search.addWidget(QLabel("🔍"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию")
        self.search_input.textChanged.connect(self._apply_filter)
        search.addWidget(self.search_input)
        layout.addLayout(search)

        # Фильтры
        filters = QHBoxLayout()

        self.filter_tag = QComboBox()
        self.filter_tag.addItem("Все теги", None)
        filters.addWidget(self.filter_tag)

        self.filter_section = QComboBox()
        self.filter_section.addItem("Все разделы", None)
        filters.addWidget(self.filter_section)

        btn = QPushButton("Применить")
        btn.clicked.connect(self._apply_filter)
        filters.addWidget(btn)

        btn_reset = QPushButton("Сбросить")
        btn_reset.clicked.connect(self._reset_filters)
        filters.addWidget(btn_reset)

        layout.addLayout(filters)

        # Список задач
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.list_widget.itemDoubleClicked.connect(self._open_task)
        layout.addWidget(self.list_widget)

        # Панель действий
        actions = QHBoxLayout()
        self.selected_label = QLabel("Выбрано: 0")
        actions.addWidget(self.selected_label)

        btn_archive = QPushButton("📦 Архивировать выбранные")
        btn_archive.clicked.connect(self._bulk_archive)
        actions.addWidget(btn_archive)

        btn_delete = QPushButton("🗑 Удалить выбранные")
        btn_delete.setStyleSheet(
            "background: #e74c3c; color: white; padding: 6px 12px; border-radius: 4px;"
        )
        btn_delete.clicked.connect(self._bulk_delete)
        actions.addWidget(btn_delete)

        layout.addLayout(actions)

        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)

    def _load_filters(self):
        # Обновить список тегов
        self.filter_tag.blockSignals(True)
        current_tag = self.filter_tag.currentData()
        self.filter_tag.clear()
        self.filter_tag.addItem("Все теги", None)
        for tag in self.vm.get_tags():
            self.filter_tag.addItem(tag.name, tag.id)
        idx = self.filter_tag.findData(current_tag)
        if idx >= 0:
            self.filter_tag.setCurrentIndex(idx)
        self.filter_tag.blockSignals(False)

        # Обновить список разделов
        self.filter_section.blockSignals(True)
        current_section = self.filter_section.currentData()
        self.filter_section.clear()
        self.filter_section.addItem("Все разделы", None)
        for sec in self.vm.get_sections():
            self.filter_section.addItem(sec.name, sec.id)
        idx = self.filter_section.findData(current_section)
        if idx >= 0:
            self.filter_section.setCurrentIndex(idx)
        self.filter_section.blockSignals(False)

    def _load_all(self):
        """Загрузить все активные задачи."""
        self._load_filters()
        tasks = self.task_repo.find_all()
        self._on_loaded(tasks)

    def _on_loaded(self, tasks):
        self.list_widget.clear()
        if not tasks:
            self.list_widget.addItem("Ничего не найдено")
            return
        for t in tasks:
            item = QListWidgetItem(
                f"●  {t.title}    [{t.progress}%]    📅 {t.deadline or '—'}"
            )
            item.setData(Qt.ItemDataRole.UserRole, t.id)
            self.list_widget.addItem(item)

    def _on_selection_changed(self):
        count = len(self.list_widget.selectedItems())
        self.selected_label.setText(f"Выбрано: {count}")

    def _apply_filter(self):
        criteria = {
            "title": self.search_input.text().strip() or None,
            "tag_id": self.filter_tag.currentData(),
            "section_id": self.filter_section.currentData(),
        }
        self.vm.apply_filter(criteria)

    def _reset_filters(self):
        """Сбросить все фильтры и показать все задачи."""
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)

        self.filter_tag.setCurrentIndex(0)
        self.filter_section.setCurrentIndex(0)

        self._load_all()

    def _open_task(self, item):
        task_id = item.data(Qt.ItemDataRole.UserRole)
        if not task_id:
            return
        from views.dialogs.task_view_dialog import TaskViewDialog
        dlg = TaskViewDialog(task_id, self)
        if dlg.exec():
            self._load_all()

    def _bulk_archive(self):
        ids = [item.data(Qt.ItemDataRole.UserRole)
               for item in self.list_widget.selectedItems()
               if item.data(Qt.ItemDataRole.UserRole)]
        if not ids:
            return
        self.task_repo.bulk_archive(ids)
        self._load_all()

    def _bulk_delete(self):
        ids = [item.data(Qt.ItemDataRole.UserRole)
               for item in self.list_widget.selectedItems()
               if item.data(Qt.ItemDataRole.UserRole)]
        if not ids:
            return
        reply = QMessageBox.question(
            self, "Удаление", f"Удалить {len(ids)} задач?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.task_repo.bulk_delete(ids)
            self._load_all()