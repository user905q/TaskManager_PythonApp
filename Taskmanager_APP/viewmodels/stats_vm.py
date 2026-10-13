from PyQt6.QtCore import QObject, pyqtSignal
from models.database import Database
from models.repositories import TimeLogRepository, BoardColumnRepository


class StatsViewModel(QObject):
    statsLoaded = pyqtSignal(dict)
    columnProgressLoaded = pyqtSignal(dict)
    columnTimeLoaded = pyqtSignal(list)
    noData = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.time_repo = TimeLogRepository()
        self.col_repo = BoardColumnRepository()

    def load_stats(self, period: str = "all"):
        cur = self.db.cursor()
        total = cur.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if total == 0:
            self.noData.emit()
            return None
        done = cur.execute("SELECT COUNT(*) FROM tasks WHERE progress=100").fetchone()[0]
        active = cur.execute("SELECT COUNT(*) FROM tasks WHERE status='active'").fetchone()[0]
        by_section = self.time_repo.get_total_by_section()
        done_period = self.time_repo.get_done_count(period)

        data = {"total": total, "done": done, "active": active,
                "by_section": by_section, "done_period": done_period}
        self.statsLoaded.emit(data)
        return data

    def load_column_progress(self):
        cur = self.db.cursor()
        columns = self.col_repo.find_all()
        result = {}
        for col in columns:
            count = cur.execute(
                "SELECT COUNT(*) FROM task_columns WHERE column_id=?", (col.id,)
            ).fetchone()[0]
            result[col.name] = {"count": count, "color": col.color,
                                 "position": col.position}
        self.columnProgressLoaded.emit(result)
        return result

    def load_column_time(self):
        data = self.time_repo.get_time_by_column()
        self.columnTimeLoaded.emit(data)
        return data