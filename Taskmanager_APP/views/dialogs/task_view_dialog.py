from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QListWidget, QListWidgetItem, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from models.repositories import (
    TaskRepository, TagRepository, AttachmentRepository, SectionRepository
)


class TaskViewDialog(QDialog):
    def __init__(self, task_id: int, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.task_repo = TaskRepository()
        self.tag_repo = TagRepository()
        self.attach_repo = AttachmentRepository()
        self.sec_repo = SectionRepository()
        self.setWindowTitle("Просмотр задачи")
        self.resize(500, 600)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        desc_box = QGroupBox("📝 Описание")
        desc_layout = QVBoxLayout(desc_box)
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        desc_layout.addWidget(self.desc_label)
        layout.addWidget(desc_box)

        meta_box = QGroupBox("Информация")
        meta_layout = QVBoxLayout(meta_box)
        self.meta_label = QLabel()
        self.meta_label.setWordWrap(True)
        meta_layout.addWidget(self.meta_label)
        layout.addWidget(meta_box)

        self.tags_label = QLabel()
        layout.addWidget(self.tags_label)

        attach_box = QGroupBox("📎 Прикреплённые файлы")
        attach_layout = QVBoxLayout(attach_box)
        self.attach_list = QListWidget()
        attach_layout.addWidget(self.attach_list)
        layout.addWidget(attach_box)

        btns = QHBoxLayout()

        btn_edit = QPushButton("Редактировать")
        btn_edit.clicked.connect(self._edit)
        btns.addWidget(btn_edit)

        btn_archive = QPushButton("📦 Архивировать")
        btn_archive.clicked.connect(self._archive)
        btns.addWidget(btn_archive)

        btn_delete = QPushButton("🗑 Удалить")
        btn_delete.setStyleSheet(
            "background: #e74c3c; color: white; padding: 6px 12px; border-radius: 4px;"
        )
        btn_delete.clicked.connect(self._delete)
        btns.addWidget(btn_delete)

        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.close)
        btns.addWidget(btn_close)

        layout.addLayout(btns)

    def _refresh_parent(self):
        """Обновить доску, если родитель — BoardView."""
        parent = self.parent()
        if parent and hasattr(parent, "vm") and hasattr(parent.vm, "load_board"):
            parent.vm.load_board()

    def _load_data(self):
        task = self.task_repo.find_by_id(self.task_id)
        if not task:
            return

        self.title_label.setText(f"📋 {task.title}")
        self.desc_label.setText(task.description or "—")

        section_name = "Без раздела"
        if task.section_id:
            for s in self.sec_repo.find_all():
                if s.id == task.section_id:
                    section_name = s.name
                    break

        self.meta_label.setText(
            f"Раздел: {section_name}\n"
            f"Прогресс: {task.progress}%\n"
            f"Срок: {task.deadline or '—'}\n"
            f"Создано: {task.created_at or '—'}"
        )

        tags = self.tag_repo.get_task_tags(self.task_id)
        self.tags_label.setText(
            "🏷 Теги: " + (", ".join(t.name for t in tags) if tags else "—")
        )

        attachments = self.attach_repo.find_by_task(self.task_id)
        self.attach_list.clear()
        if attachments:
            for a in attachments:
                item = QListWidgetItem(f"📎 {a.file_name}")
                item.setData(Qt.ItemDataRole.UserRole, a.file_path)
                self.attach_list.addItem(item)
        else:
            self.attach_list.addItem("Нет вложений")

    def _edit(self):
        from views.dialogs.task_dialog import TaskDialog
        self.close()
        dlg = TaskDialog(task_id=self.task_id)
        if dlg.exec():
            self._refresh_parent()

    def _archive(self):
        self.task_repo.archive(self.task_id)
        self._refresh_parent()
        self.accept()

    def _delete(self):
        reply = QMessageBox.question(
            self, "Удаление задачи",
            "Вы уверены, что хотите удалить задачу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.task_repo.delete(self.task_id)
            self._refresh_parent()
            self.accept()