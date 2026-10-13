from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QInputDialog, QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from viewmodels.board_vm import BoardViewModel
from views.dialogs.task_dialog import TaskDialog
from views.dialogs.section_dialog import SectionDialog
from views.dialogs.delete_section_dialog import DeleteSectionDialog
from views.dialogs.column_dialog import ColumnDialog
from views.dialogs.task_view_dialog import TaskViewDialog


class BoardView(QWidget):
    def __init__(self):
        super().__init__()
        self.vm = BoardViewModel()
        self.vm.boardLoaded.connect(self._on_board_loaded)
        self._build_ui()
        self.vm.load_board()

    # ---------- Построение UI ----------

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Верхняя панель
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>Канбан-доска</h2>"))
        header.addStretch()

        btn_new_section = QPushButton("+ Создать раздел")
        btn_new_section.clicked.connect(self._create_section)
        header.addWidget(btn_new_section)

        btn_columns = QPushButton("Колонки")
        btn_columns.clicked.connect(self._manage_columns)
        header.addWidget(btn_columns)

        layout.addLayout(header)

        # Область с колонками
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.columns_widget = QWidget()
        self.columns_layout = QHBoxLayout(self.columns_widget)
        self.columns_layout.setSpacing(12)
        self.scroll.setWidget(self.columns_widget)
        layout.addWidget(self.scroll)

        # Кнопка «+ Создать задачу» внизу
        bottom = QHBoxLayout()
        bottom.addStretch()
        btn_add_task = QPushButton("+ Создать задачу")
        btn_add_task.setStyleSheet("""
            QPushButton {
                background: #4a90e2; color: white;
                padding: 8px 20px; border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background: #3a7bc8; }
        """)
        btn_add_task.clicked.connect(lambda: self._add_task())
        bottom.addWidget(btn_add_task)
        bottom.addStretch()
        layout.addLayout(bottom)

    # ---------- Загрузка доски ----------

    def _on_board_loaded(self, columns, sections, tasks_by_section):
        while self.columns_layout.count():
            item = self.columns_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for col in columns:
            frame = self._create_column_frame(col, sections, tasks_by_section, columns)
            self.columns_layout.addWidget(frame)

    def _create_column_frame(self, col, sections, tasks_by_section, columns):
        """Колонка Канбан-доски."""
        frame = QFrame()
        frame.setMinimumWidth(280)
        frame.setStyleSheet(f"""
            QFrame {{
                background: #fafafa;
                border-top: 4px solid {col.color};
                border-radius: 8px;
            }}
        """)
        vbox = QVBoxLayout(frame)

        # Заголовок колонки
        col_header = QLabel(f"<b>{col.name}</b>")
        col_header.setStyleSheet(
            "font-size: 14px; padding: 6px; color: #2c3e50;"
        )
        vbox.addWidget(col_header)

        first_column = columns[0] if columns else None

        # В первой колонке — карточки разделов
        if first_column and col.id == first_column.id:
            for s in sections:
                tasks = tasks_by_section.get(s.id, [])
                card = self._create_section_card(s, tasks)
                vbox.addWidget(card)

            tasks_no_section = tasks_by_section.get(None, [])
            if tasks_no_section:
                card = self._create_section_card(None, tasks_no_section)
                vbox.addWidget(card)
        else:
            hint = QLabel("Перетащите задачу сюда")
            hint.setStyleSheet(
                "color: #999; padding: 20px; font-style: italic;"
            )
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(hint)

        vbox.addStretch()
        return frame

    # ---------- Карточка раздела ----------

    def _create_section_card(self, section, tasks):
        """Карточка раздела с названием и кнопками."""
        frame = QFrame()

        if section is None:
            bg = "#95a5a6"
            name = "Задачи без раздела"
        else:
            bg = section.color
            name = section.name

        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 8px;
                margin: 4px;
            }}
        """)
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(6, 6, 6, 6)

        # Заголовок с названием и кнопками
        header = QHBoxLayout()

        title = QLabel(f"<b>{name}</b>")
        title.setStyleSheet(
            "color: white; font-size: 14px; background: transparent;"
        )
        header.addWidget(title)
        header.addStretch()

        if section is not None:
            # Кнопка «Ред»
            btn_settings = QPushButton("Ред")
            btn_settings.setFixedSize(40, 26)
            btn_settings.setToolTip("Редактировать раздел")
            btn_settings.setStyleSheet("""
                QPushButton {
                    background: #ffffff;
                    color: #2c3e50;
                    font-size: 11px;
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 2px;
                }
                QPushButton:hover { background: #f0f0f0; }
            """)
            btn_settings.clicked.connect(lambda: self._edit_section(section))
            header.addWidget(btn_settings)

            # Кнопка «Удал»
            btn_del = QPushButton("Удал")
            btn_del.setFixedSize(46, 26)
            btn_del.setToolTip("Удалить раздел")
            btn_del.setStyleSheet("""
                QPushButton {
                    background: #e74c3c;
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                    padding: 2px;
                }
                QPushButton:hover { background: #c0392b; }
            """)
            btn_del.clicked.connect(lambda: self._delete_section(section.id))
            header.addWidget(btn_del)

        vbox.addLayout(header)

        # Задачи внутри карточки
        for t in tasks:
            widget = self._create_task_widget(t)
            vbox.addWidget(widget)

        # Кнопка «+ Задача» внутри карточки раздела
        btn_add = QPushButton("+ Задача")
        btn_add.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.6);
                color: #2c3e50;
                border: none;
                border-radius: 4px;
                padding: 4px;
                margin: 2px;
                font-size: 11px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.85); }
        """)
        btn_add.clicked.connect(
            lambda: self._add_task(section_id=section.id if section else None)
        )
        vbox.addWidget(btn_add)

        return frame

    # ---------- Карточка задачи ----------

    def _create_task_widget(self, t):
        """Карточка задачи с названием, датой, тегами и кнопками."""
        frame = QFrame()
        frame.setStyleSheet(
            "QFrame { background: rgba(255,255,255,0.9); "
            "border-radius: 4px; margin: 2px; }"
        )
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(6, 4, 6, 4)

        # Название + дата
        text = f"● {t.title}"
        if t.deadline:
            text += f"\n📅 {t.deadline[:16]}"
        title = QLabel(text)
        title.setStyleSheet("color: #2c3e50; background: transparent;")
        title.setWordWrap(True)
        vbox.addWidget(title)

        # Теги
        tags = self.vm.tag_repo.get_task_tags(t.id)
        if tags:
            tags_text = "Теги: " + ", ".join(tag.name for tag in tags)
            tags_label = QLabel(tags_text)
            tags_label.setStyleSheet(
                "color: #555; font-size: 10px; background: transparent;"
            )
            vbox.addWidget(tags_label)

        # Кнопки
        btns = QHBoxLayout()

        btn_open = QPushButton("Открыть")
        btn_open.setStyleSheet("""
            QPushButton {
                background: #4a90e2; color: white;
                font-size: 10px; padding: 3px 8px;
                border: none; border-radius: 3px;
            }
            QPushButton:hover { background: #3a7bc8; }
        """)
        btn_open.clicked.connect(lambda: self._open_task(t.id))
        btns.addWidget(btn_open)

        btn_del = QPushButton("Удал")
        btn_del.setFixedSize(40, 22)
        btn_del.setStyleSheet("""
            QPushButton {
                background: #e74c3c; color: white;
                font-size: 10px; font-weight: bold;
                padding: 0; border: none; border-radius: 3px;
            }
            QPushButton:hover { background: #c0392b; }
        """)
        btn_del.clicked.connect(lambda: self._delete_task(t.id))
        btns.addWidget(btn_del)

        btns.addStretch()
        vbox.addLayout(btns)
        return frame

    # ---------- Действия ----------

    def _open_task(self, task_id):
        dlg = TaskViewDialog(task_id, self)
        if dlg.exec():
            self.vm.load_board()

    def _delete_task(self, task_id):
        reply = QMessageBox.question(
            self, "Удаление", "Удалить задачу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.vm.task_repo.delete(task_id)
            self.vm.load_board()

    def _add_task(self, section_id=None):
        dlg = TaskDialog(section_id=section_id, parent=self)
        if dlg.exec():
            self.vm.load_board()

    def _create_section(self):
        dlg = SectionDialog(parent=self)
        if dlg.exec():
            self.vm.load_board()

    def _edit_section(self, section):
        name, ok = QInputDialog.getText(
            self, "Переименовать раздел", "Название:", text=section.name
        )
        if not (ok and name):
            return
        color = QColorDialog.getColor(
            QColor(section.color), self, "Выбрать цвет раздела"
        )
        color_hex = color.name() if color.isValid() else section.color
        self.vm.sec_repo.rename(section.id, name, color_hex)
        self.vm.load_board()

    def _delete_section(self, section_id):
        dlg = DeleteSectionDialog(section_id, parent=self)
        if dlg.exec():
            self.vm.load_board()

    def _manage_columns(self):
        dlg = ColumnDialog(parent=self)
        dlg.exec()
        self.vm.load_board()