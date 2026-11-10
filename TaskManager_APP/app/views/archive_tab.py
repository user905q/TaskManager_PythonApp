from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from app.viewmodels.archive_vm import ArchiveViewModel

class ArchiveTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = ArchiveViewModel()
        self.vm.data_changed.connect(self.refresh_data)
        
        layout = QVBoxLayout(self)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        self.refresh_data()

    def refresh_data(self):
        # Очищаем старые данные
        for i in reversed(range(self.container_layout.count())): 
            widget = self.container_layout.itemAt(i).widget()
            if widget: widget.setParent(None)
            
        sections, tasks = self.vm.get_archive_data()
        
        if not sections and not tasks:
            self.container_layout.addWidget(QLabel("Архив пуст"))
            return
            
        # 1. Разделы
        for s in sections:
            widget = QWidget()
            widget.setStyleSheet("background: #2C2C2C; border-radius: 4px; margin-bottom: 5px;")
            h_layout = QHBoxLayout(widget)
            
            lbl = QLabel(f"📁 Раздел: <b>{s.name}</b>")
            btn = QPushButton("Восстановить раздел")
            btn.clicked.connect(lambda checked, sec_id=s.id: self.restore_section(sec_id))
            
            h_layout.addWidget(lbl)
            h_layout.addStretch()
            h_layout.addWidget(btn)
            self.container_layout.addWidget(widget)
            
        # 2. Задачи
        for t in tasks:
            widget = QWidget()
            widget.setStyleSheet("background: #2C2C2C; border-radius: 4px; margin-bottom: 5px;")
            h_layout = QHBoxLayout(widget)
            
            lbl = QLabel(f"Задача: {t.title}")
            btn = QPushButton("Восстановить")
            btn.clicked.connect(lambda checked, task_id=t.id: self.restore_task(task_id))
            
            h_layout.addWidget(lbl)
            h_layout.addStretch()
            h_layout.addWidget(btn)
            self.container_layout.addWidget(widget)

    def restore_section(self, section_id):
        self.vm.restore_section(section_id)
        self.refresh_data()
        window = self.window()
        if hasattr(window, 'tabs'):
            window.tabs.widget(0).refresh_data()

    def restore_task(self, task_id):
        self.vm.restore_task(task_id)
        self.refresh_data()
        window = self.window()
        if hasattr(window, 'tabs'):
            window.tabs.widget(0).refresh_data()