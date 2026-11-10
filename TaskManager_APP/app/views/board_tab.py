from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from app.views.widgets.kanban_board_zone import KanbanBoardZone
from app.views.widgets.sections_zone import SectionsZone
from app.viewmodels.board_vm import BoardViewModel

class BoardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = BoardViewModel()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Верхняя зона (Канбан)
        self.board_zone = KanbanBoardZone()
        # Нижняя зона (Разделы)
        self.sections_zone = SectionsZone()

        self.splitter.addWidget(self.board_zone)
        self.splitter.addWidget(self.sections_zone)
        
        # Задаем пропорции (верх 60%, низ 40%)
        self.splitter.setSizes([600, 400])
        layout.addWidget(self.splitter)

        self.vm.data_changed.connect(self.refresh_data)
        self.refresh_data()

    def refresh_data(self):
        cols, secs = self.vm.get_board_data()
        self.board_zone.load_data(cols, secs)
        self.sections_zone.load_data(secs)