from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QTextEdit, QComboBox, 
                             QPushButton, QLabel, QHBoxLayout, QMessageBox, QDateTimeEdit, 
                             QListWidget, QFileDialog, QInputDialog, QWidget, QScrollArea, QCheckBox)
from PyQt6.QtCore import QDateTime, Qt
from app.viewmodels.task_vm import TaskViewModel
from app.models.section_repo import SectionRepo
from app.models.task_repo import TaskRepo
from app.models.entities import Task

class TaskDialog(QDialog):
    def __init__(self, parent=None, task_id=None):
        super().__init__(parent)
        self.task_id = task_id
        self.vm = TaskViewModel()
        self.vm.error_occurred.connect(self.show_error)
        
        self.setWindowTitle("Создание задачи" if not task_id else "Редактирование задачи")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        # Название
        layout.addWidget(QLabel("Название (обязательно):"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)
        
        # Описание
        layout.addWidget(QLabel("Описание:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)
        
        # Раздел
        layout.addWidget(QLabel("Раздел:"))
        self.section_combo = QComboBox()
        layout.addWidget(self.section_combo)
        self.load_sections()
        
        # Дедлайн
        deadline_layout = QHBoxLayout()
        self.use_deadline_cb = QCheckBox("Указать дедлайн")
        self.use_deadline_cb.setChecked(True) # По умолчанию включено
        self.use_deadline_cb.stateChanged.connect(self.toggle_deadline)
        deadline_layout.addWidget(self.use_deadline_cb)

        self.deadline_input = QDateTimeEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDateTime(QDateTime.currentDateTime().addDays(1))
        deadline_layout.addWidget(self.deadline_input)
        
        layout.addLayout(deadline_layout)

        
        # Теги
        layout.addWidget(QLabel("Добавить тег:"))
        tag_layout = QHBoxLayout()
        self.tags_combo = QComboBox()
        tag_layout.addWidget(self.tags_combo)
        btn_new_tag = QPushButton("Создать")
        btn_new_tag.clicked.connect(self.create_tag)
        btn_add_tag = QPushButton("Добавить")
        btn_add_tag.clicked.connect(self.add_tag_to_task)
        tag_layout.addWidget(btn_new_tag)
        tag_layout.addWidget(btn_add_tag)
        layout.addLayout(tag_layout)
        self.load_tags()

        # Список привязанных тегов (теперь через QScrollArea)
        layout.addWidget(QLabel("Привязанные теги:"))
        self.tags_scroll = QScrollArea()
        self.tags_scroll.setWidgetResizable(True)
        self.tags_scroll.setMinimumHeight(100)
        self.tags_scroll.setMaximumHeight(150)
        
        # ИСПРАВЛЕНО: убран лишний пробел
        self.tags_scroll.setStyleSheet("QScrollArea { background: transparent; border: 1px solid #444444; border-radius: 4px; }")
        
        self.tags_container = QWidget()
        self.tags_container.setStyleSheet("background: transparent;") # <-- Прозрачный фон
        self.tags_layout = QVBoxLayout(self.tags_container)
        self.tags_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tags_scroll.setWidget(self.tags_container)
        layout.addWidget(self.tags_scroll)
        
        self.load_current_tags()

        # Вложения
        layout.addWidget(QLabel("Вложения (до 10 файлов):"))
        btn_attach = QPushButton("Прикрепить файл")
        btn_attach.clicked.connect(self.attach_file)
        layout.addWidget(btn_attach)
        
        self.attachments_list = QListWidget()
        self.attachments_list.setMaximumHeight(100)
        layout.addWidget(self.attachments_list)
        
        # Заполнение полей, если это редактирование
        if self.task_id:
            task = TaskRepo.get_by_id(self.task_id)
            if task:
                self.title_input.setText(task.title)
                self.desc_input.setText(task.description or "")
                
                # Если у задачи есть дедлайн - показываем его, если нет - скрываем
                if task.deadline:
                    self.use_deadline_cb.setChecked(True)
                    self.deadline_input.setDateTime(QDateTime.fromString(task.deadline, Qt.DateFormat.ISODate))
                else:
                    self.use_deadline_cb.setChecked(False)
                    self.toggle_deadline(0) # Скрываем поле
                    
                index = self.section_combo.findData(task.section_id)
                if index >= 0:
                    self.section_combo.setCurrentIndex(index)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def toggle_deadline(self, state):
        self.deadline_input.setVisible(state == Qt.CheckState.Checked.value)

    def load_sections(self):
        sections = SectionRepo.get_all_active()
        sys_id = next((s.id for s in sections if s.is_system), None)
        self.section_combo.addItem("Без раздела", sys_id)
        for s in sections:
            if not s.is_system:
                self.section_combo.addItem(s.name, s.id)

    def load_tags(self):
        self.tags_combo.clear()
        tags = self.vm.get_all_tags()
        for t in tags:
            self.tags_combo.addItem(t.name, t.id)

    def create_tag(self):
        name, ok = QInputDialog.getText(self, "Новый тег", "Введите имя тега:")
        if ok and name:
            from app.models.tag_repo import TagRepo
            try:
                TagRepo.create(name)
                self.load_tags()
            except Exception as e:
                self.show_error(str(e))

    def attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать файл")
        if file_path:
            if self.attachments_list.count() >= 10:
                self.show_error("Достигнут лимит вложений (10).")
                return
            self.attachments_list.addItem(file_path)

    def load_current_tags(self):
        # Очищаем старый список
        for i in reversed(range(self.tags_layout.count())): 
            widget = self.tags_layout.itemAt(i).widget()
            if widget: widget.setParent(None)
            
        if not self.task_id:
            return
            
        tags = self.vm.get_tags_for_task(self.task_id)
        for t in tags:
            widget = QWidget()
            h_layout = QHBoxLayout(widget)
            h_layout.setContentsMargins(5, 2, 5, 2)
            
            lbl = QLabel(t.name)
            lbl.setStyleSheet("background: transparent;") 
            btn_del = QPushButton("X")
            btn_del.setFixedSize(20, 20)
            btn_del.setStyleSheet("background: #ef4444; color: white; border-radius: 10px; font-weight: bold;")
            btn_del.clicked.connect(lambda checked, tag_id=t.id: self.remove_tag(tag_id))
            
            h_layout.addWidget(lbl)
            h_layout.addStretch()
            h_layout.addWidget(btn_del)
            
            self.tags_layout.addWidget(widget)

    def add_tag_to_task(self):
        if not self.task_id:
            self.show_error("Сначала сохраните задачу, чтобы привязать тег.")
            return
        tag_id = self.tags_combo.currentData()
        if tag_id:
            from app.models.tag_repo import TagRepo
            TagRepo.add_to_task(self.task_id, tag_id)
            self.load_current_tags()

    def remove_tag(self, tag_id):
        if self.task_id:
            self.vm.remove_tag_from_task(self.task_id, tag_id)
            self.load_current_tags()

    def save(self):
        title = self.title_input.text()
        desc = self.desc_input.toPlainText()
        section_id = self.section_combo.currentData()
        
        # Если галочка стоит - берем дату, если нет - передаем None
        deadline_dt = None
        if self.use_deadline_cb.isChecked():
            deadline_dt = self.deadline_input.dateTime().toPyDateTime()
        
        if self.task_id:
            try:
                self.vm.update_task(self.task_id, title, desc, section_id, deadline_dt)
                self.accept()
            except Exception as e:
                self.show_error(str(e))
        else:
            task = Task(title=title, description=desc, section_id=section_id, deadline=deadline_dt)
            try:
                new_task_id = TaskRepo.create(task)
                for i in range(self.attachments_list.count()):
                    filepath = self.attachments_list.item(i).text()
                    self.vm.add_attachment(new_task_id, filepath)

                self.accept()
            except Exception as e:
                self.show_error(str(e))

    def show_error(self, msg):
        QMessageBox.warning(self, "Ошибка", msg)