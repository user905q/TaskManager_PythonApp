from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit, QComboBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox, QDateTimeEdit,
    QFileDialog, QInputDialog
)
from PyQt6.QtCore import QDateTime
from viewmodels.task_vm import TaskViewModel
from models.repositories import AttachmentRepository, SectionRepository, TagRepository


class TaskDialog(QDialog):
    def __init__(self, section_id=None, task_id=None, parent=None):
        super().__init__(parent)
        self.vm = TaskViewModel()
        self.section_id = section_id
        self.task_id = task_id
        self.attachments = []
        self.setWindowTitle("Новая задача" if not task_id else "Редактировать задачу")
        self.resize(500, 600)
        self._build_ui()
        if task_id:
            self._load_task()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Название *"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Описание"))
        self.desc_input = QTextEdit()
        layout.addWidget(self.desc_input)

        # Раздел
        layout.addWidget(QLabel("Раздел"))
        self.section_combo = QComboBox()
        self.section_combo.addItem("Без раздела", None)
        for s in SectionRepository().find_all():
            self.section_combo.addItem(s.name, s.id)
        if self.section_id:
            idx = self.section_combo.findData(self.section_id)
            if idx >= 0:
                self.section_combo.setCurrentIndex(idx)
        layout.addWidget(self.section_combo)

        # Теги
        layout.addWidget(QLabel("Тег"))
        tag_row = QHBoxLayout()
        self.tag = QComboBox()
        self._reload_tags()
        tag_row.addWidget(self.tag)

        btn_new_tag = QPushButton("+ Создать новый тег")
        btn_new_tag.clicked.connect(self._create_new_tag)
        tag_row.addWidget(btn_new_tag)
        layout.addLayout(tag_row)

        # Срок
        layout.addWidget(QLabel("Срок выполнения"))
        self.deadline = QDateTimeEdit(QDateTime.currentDateTime())
        self.deadline.setCalendarPopup(True)
        layout.addWidget(self.deadline)

        # Вложения
        layout.addWidget(QLabel("Вложения (до 10 файлов)"))
        self.attach_label = QLabel("Файлов: 0")
        layout.addWidget(self.attach_label)
        btn_attach = QPushButton("+ Прикрепить файл")
        btn_attach.clicked.connect(self._attach_file)
        layout.addWidget(btn_attach)

        # Кнопки
        btns = QHBoxLayout()
        cancel = QPushButton("Отмена")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Сохранить")
        save.clicked.connect(self._save)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        layout.addLayout(btns)

    def _reload_tags(self):
        current_id = self.tag.currentData() if self.tag.count() > 0 else None
        self.tag.clear()
        for t in self.vm.get_all_tags():
            self.tag.addItem(t.name, t.id)
        if current_id is not None:
            idx = self.tag.findData(current_id)
            if idx >= 0:
                self.tag.setCurrentIndex(idx)

    def _create_new_tag(self):
        name, ok = QInputDialog.getText(
            self, "Новый тег", "Введите название тега:"
        )
        if not ok or not name.strip():
            return
        tag_repo = TagRepository()
        try:
            tag_repo.create(name.strip(), "#9b59b6")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать тег: {e}")
            return
        self._reload_tags()
        idx = self.tag.findText(name.strip())
        if idx >= 0:
            self.tag.setCurrentIndex(idx)

    def _load_task(self):
        """Заполнить поля данными существующей задачи."""
        task = self.vm.repo.find_by_id(self.task_id)
        if not task:
            return

        self.title_input.setText(task.title)
        self.desc_input.setText(task.description or "")

        if task.section_id:
            idx = self.section_combo.findData(task.section_id)
            if idx >= 0:
                self.section_combo.setCurrentIndex(idx)

        if task.deadline:
            dt = QDateTime.fromString(task.deadline, "yyyy-MM-dd HH:mm:ss")
            if dt.isValid():
                self.deadline.setDateTime(dt)

        tags = self.vm.get_task_tags(self.task_id)
        if tags:
            idx = self.tag.findData(tags[0].id)
            if idx >= 0:
                self.tag.setCurrentIndex(idx)

    def _attach_file(self):
        if len(self.attachments) >= 10:
            QMessageBox.warning(self, "Лимит", "Достигнут лимит вложений (10)")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать файл")
        if path:
            self.attachments.append(path)
            self.attach_label.setText(f"Файлов: {len(self.attachments)}")

    def _save(self):
        try:
            data = {
                "title": self.title_input.text().strip(),
                "description": self.desc_input.toPlainText(),
                "section_id": self.section_combo.currentData(),
                "deadline": self.deadline.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            }

            if self.task_id:
                self.vm.update_task(self.task_id, data)
                task_id = self.task_id
                # Удалить старые теги
                self.vm.tag_repo.unlink_all(task_id)
            else:
                task_id = self.vm.create_task(data)

            # Вложения
            att_repo = AttachmentRepository()
            for path in self.attachments:
                att_repo.attach_file(task_id, path)

            # Тег
            tag_id = self.tag.currentData()
            if tag_id:
                self.vm.tag_repo.link_to_task(task_id, tag_id)

            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))