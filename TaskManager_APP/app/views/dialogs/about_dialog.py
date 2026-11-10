from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from app.config import DATA_DIR

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h3>Task Manager</h3>"))
        layout.addWidget(QLabel("Автор: Оралов Кирилл Александрович"))
        layout.addWidget(QLabel(f"Папка с данными:\n{DATA_DIR}"))
        
        btn = QPushButton("Закрыть")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)