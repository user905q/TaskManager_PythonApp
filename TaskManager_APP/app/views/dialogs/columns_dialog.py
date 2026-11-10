from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QPushButton, QInputDialog, QMessageBox)
from app.models.column_repo import ColumnRepo

class ColumnsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление колонками")
        self.setMinimumSize(300, 400)
        
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.add_column)
        
        btn_rename = QPushButton("Переименовать")
        btn_rename.clicked.connect(self.rename_column)
        
        btn_delete = QPushButton("Удалить")
        btn_delete.clicked.connect(self.delete_column)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_rename)
        btn_layout.addWidget(btn_delete)
        layout.addLayout(btn_layout)
        
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.load_columns()

    def load_columns(self):
        self.list_widget.clear()
        cols = ColumnRepo.get_all()
        for c in cols:
            item = QListWidgetItem(c.name)
            item.setData(1, c.id) # Сохраняем ID колонки
            self.list_widget.addItem(item)

    def add_column(self):
        name, ok = QInputDialog.getText(self, "Новая колонка", "Введите название:")
        if ok and name:
            try:
                ColumnRepo.create_column(name)
                self.load_columns()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def rename_column(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        col_id = item.data(1)
        new_name, ok = QInputDialog.getText(self, "Переименовать", "Новое название:", text=item.text())
        if ok and new_name:
            try:
                ColumnRepo.rename_column(col_id, new_name)
                self.load_columns()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def delete_column(self):
        item = self.list_widget.currentItem()
        if not item: return
        
        col_id = item.data(1)
        try:
            ColumnRepo.delete_column(col_id)
            self.load_columns()
            QMessageBox.information(self, "Успех", "Колонка удалена. Задачи перенесены в первую колонку.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))