from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout, QMenu, QMessageBox
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QPainter, QColor, QPen 
from app.models.entities import Section 

class DotsButton(QPushButton):
    """Кнопка с тремя точками, нарисованными вручную"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Убираем стандартный стиль, чтобы он не перекрывал нашу отрисовку
        self.setStyleSheet("background: transparent; border: none;") 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Цвет точек (оранжевый)
        painter.setBrush(QColor("#F97316"))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Рисуем три точки по центру
        cx = self.width() // 2
        cy = self.height() // 2
        radius = 2
        spacing = 6
        
        painter.drawEllipse(QPoint(cx, cy - spacing), radius, radius)
        painter.drawEllipse(QPoint(cx, cy), radius, radius)
        painter.drawEllipse(QPoint(cx, cy + spacing), radius, radius)


class SectionCard(QFrame):
    def __init__(self, section: Section, progress: int, parent=None):
        super().__init__(parent)
        self.section_id = section.id
        self.is_system = section.is_system
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        self.setStyleSheet(f"SectionCard {{ border-top: 4px solid {section.color}; }}")
        
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        title = QLabel(section.name)
        title.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        prog_lbl = QLabel(f"{progress}%")
        prog_lbl.setProperty("class", "section_progress") 
        header_layout.addWidget(prog_lbl)
        
        if not self.is_system:
            self.menu_btn = DotsButton()
            self.menu_btn.setFixedSize(24, 24)
            self.menu_btn.setObjectName("section_menu_btn") 
            self.menu_btn.clicked.connect(self.show_menu)
            header_layout.addWidget(self.menu_btn)
            
        layout.addLayout(header_layout)
        
        btn_add = QPushButton("+ задача")
        btn_add.setObjectName("btn_add") 
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.add_task_to_section)
        layout.addWidget(btn_add)
        
        self.tasks_list = QListWidget()
        self.tasks_list.setObjectName("section_task_list") 
        layout.addWidget(self.tasks_list)

    def add_task_to_section(self):
        from app.views.dialogs.task_dialog import TaskDialog
        dialog = TaskDialog(self.window())
        index = dialog.section_combo.findData(self.section_id)
        if index >= 0:
            dialog.section_combo.setCurrentIndex(index)
        if dialog.exec():
            self.refresh_parent_board()

    def show_menu(self):
        menu = QMenu(self)
        action_edit = QAction("Редактировать", self)
        action_edit.triggered.connect(self.edit_section)
        menu.addAction(action_edit)
        
        action_archive = QAction("В архив", self)
        action_archive.triggered.connect(self.archive_section) 
        menu.addAction(action_archive)
        
        action_delete = QAction("Удалить", self)
        action_delete.triggered.connect(self.delete_section)
        menu.addAction(action_delete)
        
        # menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))
        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def archive_section(self):
        from app.viewmodels.section_vm import SectionViewModel
        vm = SectionViewModel()
        vm.archive_section(self.section_id)
        self.refresh_parent_board()

    def edit_section(self):
        from app.views.dialogs.section_dialog import SectionDialog
        dialog = SectionDialog(self.window(), section_id=self.section_id)
        if dialog.exec():
            self.refresh_parent_board()

    def delete_section(self):
        msg_box = QMessageBox(self.window())
        msg_box.setWindowTitle("Удаление раздела")
        msg_box.setText("Вы уверены, что хотите удалить раздел?")
        msg_box.setInformativeText("Выберите, что сделать с задачами внутри:")
        
        btn_with_tasks = msg_box.addButton("Удалить с задачами", QMessageBox.ButtonRole.DestructiveRole)
        btn_only = msg_box.addButton("Задачи в 'Без раздела'", QMessageBox.ButtonRole.ActionRole)
        btn_cancel = msg_box.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_cancel:
            return
            
        from app.viewmodels.section_vm import SectionViewModel
        vm = SectionViewModel()
        
        if msg_box.clickedButton() == btn_with_tasks:
            vm.delete_section(self.section_id, delete_tasks=True)
        else:
            vm.delete_section(self.section_id, delete_tasks=False)
            
        self.refresh_parent_board()

    def refresh_parent_board(self):
        window = self.window()
        if hasattr(window, 'tabs'):
            window.tabs.widget(0).refresh_data()
            if hasattr(window.tabs.widget(1), 'load_tasks'):
                window.tabs.widget(1).load_tasks()
            if hasattr(window.tabs.widget(2), 'load_data'): 
                window.tabs.widget(2).load_data()