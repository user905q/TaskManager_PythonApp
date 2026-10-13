from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QHBoxLayout, QMessageBox, QColorDialog
)
from PyQt6.QtGui import QColor
from models.repositories import SectionRepository
from models.entities import Section


class SectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repo = SectionRepository()
        self.color = "#4a90e2"
        self.setWindowTitle("Новый раздел")
        self.resize(400, 250)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Название раздела *"))
        self.name = QLineEdit()
        layout.addWidget(self.name)

        # Выбор цвета
        layout.addWidget(QLabel("Цвет раздела:"))
        color_row = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(60, 30)
        self.color_btn.setStyleSheet(f"background: {self.color}; border-radius: 4px;")
        self.color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self.color_btn)
        color_row.addWidget(QLabel("Нажмите, чтобы выбрать цвет"))
        color_row.addStretch()
        layout.addLayout(color_row)

        btns = QHBoxLayout()
        cancel = QPushButton("Отмена")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Создать")
        save.clicked.connect(self._save)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        layout.addLayout(btns)

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self.color), self, "Выбрать цвет")
        if color.isValid():
            self.color = color.name()
            self.color_btn.setStyleSheet(
                f"background: {self.color}; border-radius: 4px;"
            )

    def _save(self):
        try:
            section = Section(name=self.name.text().strip(), color=self.color)
            self.repo.create(section)
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))