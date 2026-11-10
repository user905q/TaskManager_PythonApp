from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from app.models.task_repo import TaskRepo
from app.models.tag_repo import TagRepo
from app.models.attachment_repo import AttachmentRepo
from app.models.section_repo import SectionRepo
from app.config import STORAGE_DIR
import os
import subprocess
import sys
from datetime import datetime

class TaskViewDialog(QDialog):
    def __init__(self, task_id, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.setWindowTitle("Просмотр задачи")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        task = TaskRepo.get_by_id(task_id)
        if not task:
            layout.addWidget(QLabel("Задача не найдена"))
            return
            
        # Название
        title = QLabel(f"<h2>{task.title}</h2>")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Раздел
        sections = SectionRepo.get_all_active()
        sec_name = next((s.name for s in sections if s.id == task.section_id), "Без раздела")
        layout.addWidget(QLabel(f"<b>Раздел:</b> {sec_name}"))
        
        # Дедлайн (исправлено: добавлена проверка на None)
        if task.deadline:
            if isinstance(task.deadline, str):
                try:
                    dt = datetime.fromisoformat(task.deadline)
                except ValueError:
                    dt = None
            else:
                dt = task.deadline
                
            if dt:
                layout.addWidget(QLabel(f"<b>Дедлайн:</b> {dt.strftime('%d.%m.%Y %H:%M')}"))
            else:
                layout.addWidget(QLabel(f"<b>Дедлайн:</b> {task.deadline}"))
            
        # Описание
        if task.description:
            layout.addWidget(QLabel("<b>Описание:</b>"))
            desc = QLabel(task.description)
            desc.setWordWrap(True)
            desc.setStyleSheet("background: #f3f4f6; padding: 5px; border-radius: 4px;")
            layout.addWidget(desc)
            
        # Теги
        tags = TagRepo.get_for_task(task_id)
        if tags:
            tag_text = ", ".join([t.name for t in tags])
            layout.addWidget(QLabel(f"<b>Теги:</b> {tag_text}"))
            
        # Вложения
        attachments = AttachmentRepo.get_for_task(task_id)
        if attachments:
            layout.addWidget(QLabel("<b>Вложения:</b>"))
            att_list = QListWidget()
            att_list.setMaximumHeight(100)
            for att in attachments:
                att_list.addItem(att.original_name)
            layout.addWidget(att_list)
            
            # Кнопка открытия первого файла
            btn_open = QPushButton("Открыть первый файл")
            btn_open.clicked.connect(lambda: self.open_file(attachments[0].stored_name))
            layout.addWidget(btn_open)

        # Кнопка закрытия
        btn_close = QPushButton("Закрыть")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def open_file(self, stored_name):
        filepath = STORAGE_DIR / stored_name
        if filepath.exists():
            if sys.platform == 'win32':
                os.startfile(filepath)
            else:
                subprocess.call(('xdg-open', str(filepath)))