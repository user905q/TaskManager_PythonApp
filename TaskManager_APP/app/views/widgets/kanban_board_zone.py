from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal
from app.views.widgets.task_card import TaskCard

class KanbanColumnWidget(QWidget):
    task_dropped = pyqtSignal(int, int) # task_id, new_column_id

    def __init__(self, column_id, name, parent=None):
        super().__init__(parent)
        self.column_id = column_id
        self.setAcceptDrops(True) # Разрешаем принимать дропы
        
        self.setFixedWidth(280)
        # self.setStyleSheet("KanbanColumnWidget { background: transparent; border: 1px solid #d1d5db; border-radius: 8px; padding: 5px; }")
        
        self.layout = QVBoxLayout(self)
        
        title = QLabel(name)
        # title.setStyleSheet("font-weight: bold; font-size: 14px; border: none; padding-bottom: 5px;")
        self.layout.addWidget(title)
        
        self.tasks_layout = QVBoxLayout()
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addLayout(self.tasks_layout)
        self.layout.addStretch() # Прижимаем карточки к верху

    def add_task(self, task_card):
        self.tasks_layout.addWidget(task_card)

    # --- ЛОГИКА ПРИЕМА ДРОПА ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            task_id = int(event.mimeData().text())
            self.task_dropped.emit(task_id, self.column_id)
            event.acceptProposedAction()

class KanbanBoardZone(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def load_data(self, columns_data, sections_data):
        # Очистка
        for i in reversed(range(self.container_layout.count())): 
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        sections_dict = {s['section'].id: s['section'].name for s in sections_data}

        for col_data in columns_data:
            col_widget = KanbanColumnWidget(col_data['column']['id'], col_data['column']['name'])
            col_widget.task_dropped.connect(self.on_task_dropped)
            
            for t_data in col_data['tasks']:
                task = t_data['task']
                progress = t_data['progress']
                sec_name = sections_dict.get(task.section_id, "Без раздела")
                
                card = TaskCard(task, progress, sec_name)
                col_widget.add_task(card)
                
            self.container_layout.addWidget(col_widget)

    def on_task_dropped(self, task_id, new_column_id):
        # Ищем BoardTab (родительскую вкладку) и вызываем move_task
        parent = self.parent()
        while parent:
            if hasattr(parent, 'vm'):
                parent.vm.move_task(task_id, new_column_id)
                break
            parent = parent.parent()