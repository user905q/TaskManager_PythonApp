from PyQt6.QtWidgets import QWidget, QScrollArea, QGridLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from app.views.widgets.section_card import SectionCard

class SectionsZone(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")  # <-- Прозрачность для темной темы
        self.grid = QGridLayout(self.container)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

    def load_data(self, sections_data):
        # Очистка старых карточек
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            
        row, col = 0, 0
        for sec_data in sections_data:
            card = SectionCard(sec_data['section'], sec_data['progress'])
            
            # Добавляем задачи в карточку раздела
            for t_data in sec_data['tasks']:
                t = t_data['task']
                card.tasks_list.addItem(f"{t.title} ({t_data['progress']}%)")
            
            # 3 в ряд
            self.grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1