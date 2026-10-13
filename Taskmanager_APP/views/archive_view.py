from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QListWidget,
    QListWidgetItem, QHBoxLayout, QPushButton
)
from viewmodels.archive_vm import ArchiveViewModel
from models.database import Database


class ArchiveView(QWidget):
    def __init__(self):
        super().__init__()
        self.vm = ArchiveViewModel()
        self.db = Database()
        self.vm.archiveLoaded.connect(self._on_loaded)
        self._build_ui()
        self.vm.load_archive()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.sections_box = QGroupBox("Архивированные разделы")
        self.sections_layout = QVBoxLayout(self.sections_box)
        layout.addWidget(self.sections_box)

        self.tasks_box = QGroupBox("Архивированные задачи")
        self.tasks_list = QListWidget()
        vbox = QVBoxLayout(self.tasks_box)
        vbox.addWidget(self.tasks_list)
        layout.addWidget(self.tasks_box)

    def _on_loaded(self, tasks, sections):
        for i in reversed(range(self.sections_layout.count())):
            w = self.sections_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        self.tasks_list.clear()

        # Разделы
        for sec in sections:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"📁 {sec['name']}"))
            btn = QPushButton("↩ Восстановить")
            btn.clicked.connect(lambda _, sid=sec["id"]: self._restore_section(sid))
            row.addWidget(btn)
            wrapper = QWidget()
            wrapper.setLayout(row)
            self.sections_layout.addWidget(wrapper)

        # Задачи
        cur = self.db.cursor()
        for t in tasks:
            section_name = "Задача без раздела"
            if t.section_id:
                s = cur.execute("SELECT name FROM sections WHERE id=?",
                                (t.section_id,)).fetchone()
                if s:
                    section_name = s["name"]

            row = QHBoxLayout()
            row.addWidget(QLabel(f"✓ {t.title}   [{section_name}]"))
            btn = QPushButton("↩ Восстановить")
            btn.clicked.connect(lambda _, tid=t.id: self._restore_task(tid))
            row.addWidget(btn)

            wrapper = QWidget()
            wrapper.setLayout(row)
            item = QListWidgetItem()
            self.tasks_list.addItem(item)
            self.tasks_list.setItemWidget(item, wrapper)

    def _restore_task(self, task_id):
        self.vm.restore_task(task_id)
        self.vm.load_archive()

    def _restore_section(self, section_id):
        self.vm.restore_section(section_id)
        self.vm.load_archive()