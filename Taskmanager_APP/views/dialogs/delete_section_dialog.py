from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QRadioButton, QPushButton,
    QLabel, QHBoxLayout
)
from models.repositories import SectionRepository


class DeleteSectionDialog(QDialog):
    def __init__(self, section_id, parent=None):
        super().__init__(parent)
        self.section_id = section_id
        self.repo = SectionRepository()
        self.setWindowTitle("Удаление раздела")
        self.resize(450, 200)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Что сделать с задачами раздела?"))
        self.rb_with = QRadioButton("Удалить раздел вместе со всеми задачами")
        self.rb_only = QRadioButton(
            "Удалить только раздел — задачи переходят в «Задачи без раздела»"
        )
        self.rb_with.setChecked(True)
        layout.addWidget(self.rb_with)
        layout.addWidget(self.rb_only)

        btns = QHBoxLayout()
        cancel = QPushButton("Отмена")
        cancel.clicked.connect(self.reject)
        delete = QPushButton("Удалить")
        delete.clicked.connect(self._delete)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(delete)
        layout.addLayout(btns)

    def _delete(self):
        if self.rb_with.isChecked():
            self.repo.delete_with_tasks(self.section_id)
        else:
            self.repo.delete_only(self.section_id)
        self.accept()