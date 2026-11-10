from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar, QPushButton, QMenu, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QAction, QPainter, QColor, QPen
from app.models.entities import Task

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

class TaskCard(QFrame):
    def __init__(self, task: Task, progress: int, section_name: str = "", tags: list = None, parent=None):
        super().__init__(parent)
        self.task_id = task.id
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        header_layout = QHBoxLayout()
        title = QLabel(task.title)
        title.setStyleSheet("font-weight: bold; border: none;") 
        title.setWordWrap(True) 
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.menu_btn = DotsButton() 
        self.menu_btn.setFixedSize(24, 24)
        self.menu_btn.setObjectName("task_menu_btn") 
        self.menu_btn.clicked.connect(self.show_menu)
        header_layout.addWidget(self.menu_btn)
        layout.addLayout(header_layout)

        if section_name:
            sec = QLabel(f"📁 {section_name}")
            sec.setProperty("class", "task_subtext") 
            layout.addWidget(sec)
            
        if task.deadline:
            dl_text = str(task.deadline)[:16] 
            dl = QLabel(f"⏰ {dl_text}")
            dl.setProperty("class", "task_deadline") 
            layout.addWidget(dl)
            
        if tags:
            tg = QLabel(f"🏷️ {', '.join(tags)}")
            tg.setProperty("class", "task_subtext") 
            layout.addWidget(tg)

        pb = QProgressBar()
        pb.setValue(progress)
        pb.setTextVisible(False)
        pb.setFixedHeight(5)
        layout.addWidget(pb)
        
        lbl_prog = QLabel(f"{progress}%")
        lbl_prog.setProperty("class", "task_subtext") 
        layout.addWidget(lbl_prog)

    def show_menu(self):
        menu = QMenu(self)
        # Стили меню берутся из QSS
        action_edit = QAction("Редактировать", self)
        action_edit.triggered.connect(self.edit_task)
        menu.addAction(action_edit)
        
        action_archive = QAction("В архив", self)
        action_archive.triggered.connect(self.archive_task)
        menu.addAction(action_archive)
        
        action_delete = QAction("Удалить", self)
        action_delete.triggered.connect(self.delete_task)
        menu.addAction(action_delete)
        
        # menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))
        menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def edit_task(self):
        from app.views.dialogs.task_dialog import TaskDialog
        dialog = TaskDialog(self.window(), task_id=self.task_id)
        if dialog.exec():
            self.refresh_views()

    def archive_task(self):
        from app.viewmodels.task_vm import TaskViewModel
        vm = TaskViewModel()
        vm.archive_task(self.task_id)
        self.refresh_views()

    def delete_task(self):
        reply = QMessageBox.question(self.window(), 'Удаление', 'Вы уверены, что хотите удалить задачу навсегда?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from app.viewmodels.task_vm import TaskViewModel
            vm = TaskViewModel()
            vm.delete_task(self.task_id)
            self.refresh_views()

    def refresh_views(self):
        window = self.window()
        if hasattr(window, 'board_tab'): window.board_tab.refresh_data()
        if hasattr(window, 'feed_tab'): window.feed_tab.load_tasks()
        if hasattr(window, 'stats_tab'): window.stats_tab.load_data()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(str(self.task_id))
            drag.setMimeData(mime)
            
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.position().toPoint())
            
            drag.exec(Qt.DropAction.MoveAction)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            from app.views.dialogs.task_view_dialog import TaskViewDialog
            dialog = TaskViewDialog(self.task_id, self.window())
            dialog.exec()