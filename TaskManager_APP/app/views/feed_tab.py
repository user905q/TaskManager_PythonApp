from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QComboBox, QPushButton, QListWidget, QListWidgetItem, QLabel)
from PyQt6.QtCore import Qt
from app.viewmodels.feed_vm import FeedViewModel
from app.models.section_repo import SectionRepo
from app.models.tag_repo import TagRepo
from app.db.connection import get_connection
from app.models.column_repo import ColumnRepo
from app.views.widgets.task_card import TaskCard

class FeedTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = FeedViewModel()
        
        layout = QVBoxLayout(self)
        
        # --- Фильтры ---
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию...")
        filter_layout.addWidget(self.search_input)
        
        self.section_combo = QComboBox()
        self.section_combo.addItem("Все разделы", None)
        for s in SectionRepo.get_all_active():
            self.section_combo.addItem(s.name, s.id)
        filter_layout.addWidget(self.section_combo)
        
        self.btn_search = QPushButton("Найти")
        self.btn_search.clicked.connect(self.load_tasks)
        filter_layout.addWidget(self.btn_search)
        
        layout.addLayout(filter_layout)
        
        # --- Список задач ---
        self.tasks_list = QListWidget()
        self.tasks_list.setStyleSheet("QListWidget { border: none; background: transparent; }")
        layout.addWidget(self.tasks_list)
        
        self.load_tasks()

    def load_tasks(self):
        self.tasks_list.clear()
        search_text = self.search_input.text()
        section_id = self.section_combo.currentData()
        
        tasks = self.vm.get_filtered_tasks(search_text=search_text, section_id=section_id)
        
        if not tasks:
            self.tasks_list.addItem("По запросу ничего не найдено")
            return

        sections = {s.id: s.name for s in SectionRepo.get_all_active()}
        
        # Получаем данные о колонках для расчета прогресса
        with get_connection() as conn:
            cols = conn.execute("SELECT * FROM board_columns ORDER BY position").fetchall()
            total_cols = len(cols)

        for t in tasks:
            item = QListWidgetItem()
            sec_name = sections.get(t.section_id, "Без раздела")
            
            # Считаем реальный прогресс
            prog = 0
            with get_connection() as conn:
                tc = conn.execute("SELECT column_id FROM task_columns WHERE task_id = ?", (t.id,)).fetchone()
                if tc:
                    col_pos = next((c["position"] for c in cols if c["id"] == tc["column_id"]), 0)
                    prog = ColumnRepo.calculate_progress(col_pos + 1, total_cols)

            # Получаем теги для этой задачи
            tags = [tag.name for tag in TagRepo.get_for_task(t.id)]

            # Создаем карточку с тегами
            card = TaskCard(t, progress=prog, section_name=sec_name, tags=tags)
            item.setSizeHint(card.sizeHint())
            self.tasks_list.addItem(item)
            self.tasks_list.setItemWidget(item, card)