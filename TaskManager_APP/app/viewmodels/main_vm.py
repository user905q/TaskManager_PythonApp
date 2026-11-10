from PyQt6.QtCore import QObject

class MainViewModel(QObject):
    def __init__(self):
        super().__init__()
        # Здесь мы позже свяжем сигналы всех VM между собой
        pass