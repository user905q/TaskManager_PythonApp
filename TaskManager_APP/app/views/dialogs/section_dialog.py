from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QHBoxLayout, QMessageBox, QColorDialog)
from PyQt6.QtGui import QColor
from app.viewmodels.section_vm import SectionViewModel
from app.models.section_repo import SectionRepo
from app.models.entities import Section

class SectionDialog(QDialog):
    def __init__(self, parent=None, section_id=None):
        super().__init__(parent)
        self.section_id = section_id
        self.vm = SectionViewModel()
        self.vm.error_occurred.connect(self.show_error)
        
        self.setWindowTitle("Создание раздела" if not section_id else "Редактирование раздела")
        self.setMinimumWidth(300)
        
        self.current_color = "#3B82F6"
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Название раздела:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Цвет раздела:"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 25)
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        # Заполняем данные, если это редактирование
        if self.section_id:
            from app.models.section_repo import SectionRepo
            sections = SectionRepo.get_all_active()
            sec = next((s for s in sections if s.id == self.section_id), None)
            if sec:
                self.name_input.setText(sec.name)
                self.current_color = sec.color
                
        self.update_color_btn()
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def update_color_btn(self):
        self.color_btn.setStyleSheet(f"background-color: {self.current_color}; border: 1px solid #ccc;")

    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.current_color), self, "Выберите цвет")
        if color.isValid():
            self.current_color = color.name()
            self.update_color_btn()

    def save(self):
        name = self.name_input.text()
        if self.section_id:
            self.vm.update_section(self.section_id, name, self.current_color)
        else:
            self.vm.create_section(name, self.current_color)
        self.accept()

    def show_error(self, msg):
        QMessageBox.warning(self, "Ошибка", msg)