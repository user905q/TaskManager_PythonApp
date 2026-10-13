from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QInputDialog, QMessageBox
)
from viewmodels.board_vm import BoardViewModel


class ColumnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = BoardViewModel()
        self.setWindowTitle("Управление колонками")
        self.resize(500, 400)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Колонки (максимум 10):"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btns = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_add.clicked.connect(self._add)
        btn_rename = QPushButton("✏ Переименовать")
        btn_rename.clicked.connect(self._rename)
        btn_del = QPushButton("🗑 Удалить")
        btn_del.clicked.connect(self._delete)
        btns.addWidget(btn_add)
        btns.addWidget(btn_rename)
        btns.addWidget(btn_del)
        layout.addLayout(btns)

        close = QPushButton("Закрыть")
        close.clicked.connect(self.accept)
        layout.addWidget(close)

    def _load(self):
        self.list_widget.clear()
        cols = self.vm.col_repo.find_all()
        for c in cols:
            self.list_widget.addItem(f"{c.position}. {c.name}")
        self.setWindowTitle(f"Управление колонками (осталось: {10 - len(cols)} из 10)")

    def _add(self):
        name, ok = QInputDialog.getText(self, "Новая колонка", "Название:")
        if ok and name:
            if not self.vm.create_column(name):
                QMessageBox.warning(self, "Лимит", "Достигнут лимит колонок (10)")
            self._load()

    def _rename(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        name, ok = QInputDialog.getText(self, "Переименовать", "Новое название:")
        if ok and name:
            cols = self.vm.col_repo.find_all()
            idx = self.list_widget.currentRow()
            self.vm.rename_column(cols[idx].id, name)
            self._load()

    def _delete(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        cols = self.vm.col_repo.find_all()
        idx = self.list_widget.currentRow()
        self.vm.delete_column(cols[idx].id)
        self._load()