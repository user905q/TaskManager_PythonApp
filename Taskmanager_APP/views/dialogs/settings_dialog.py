from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QRadioButton, QPushButton,
    QHBoxLayout, QLabel
)
from viewmodels.settings_vm import SettingsViewModel


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = SettingsViewModel()
        self.setWindowTitle("Настройки")
        self.resize(350, 180)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Тема оформления:"))
        self.rb_light = QRadioButton("Светлая")
        self.rb_dark = QRadioButton("Тёмная")
        current = self.vm.get_theme()
        (self.rb_dark if current == "dark" else self.rb_light).setChecked(True)
        layout.addWidget(self.rb_light)
        layout.addWidget(self.rb_dark)

        btns = QHBoxLayout()
        cancel = QPushButton("Отмена")
        cancel.clicked.connect(self.reject)
        apply = QPushButton("Применить")
        apply.clicked.connect(self._apply)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(apply)
        layout.addLayout(btns)

    def _apply(self):
        theme = "dark" if self.rb_dark.isChecked() else "light"
        self.vm.set_theme(theme)
        self.accept()