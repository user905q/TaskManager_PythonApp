from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from models.repositories import (
    BoardColumnRepository, SectionRepository,
    TaskRepositoryExtended, TagRepository
)
from models.entities import BoardColumn


class BoardViewModel(QObject):
    boardLoaded = pyqtSignal(list, list, dict)
    columnCreated = pyqtSignal(object)
    columnRenamed = pyqtSignal(int, str)
    columnDeleted = pyqtSignal(int)
    taskMoved = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.col_repo = BoardColumnRepository()
        self.sec_repo = SectionRepository()
        self.task_repo = TaskRepositoryExtended()
        self.tag_repo = TagRepository()          # ← ЭТО
        self.db = self.col_repo.db

    def load_board(self):
        columns = self.col_repo.find_all()
        sections = self.sec_repo.find_all()
        tasks_by_section = {}
        for s in sections:
            tasks_by_section[s.id] = self.task_repo.find_by_section(s.id)
        tasks_by_section[None] = self.task_repo.find_by_section(None)
        self.boardLoaded.emit(columns, sections, tasks_by_section)
        return columns, sections, tasks_by_section

    def create_column(self, name: str) -> bool:
        if self.col_repo.count() >= 10:
            return False
        col_id = self.col_repo.create(name)
        self.columnCreated.emit(BoardColumn(id=col_id, name=name))
        return True

    def rename_column(self, column_id: int, new_name: str):
        self.col_repo.rename(column_id, new_name)
        self.columnRenamed.emit(column_id, new_name)

    def delete_column(self, column_id: int):
        self.col_repo.delete(column_id)
        self.columnDeleted.emit(column_id)

    def move_task_to_column(self, task_id: int, column_id: int):
        cur = self.db.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            UPDATE time_logs 
            SET ended_at = ?, 
                duration_sec = strftime('%s', ?) - strftime('%s', started_at)
            WHERE task_id = ? AND ended_at IS NULL
        """, (now, now, task_id))

        cur.execute("""
            INSERT INTO time_logs (task_id, column_id, started_at)
            VALUES (?, ?, ?)
        """, (task_id, column_id, now))

        cur.execute("""
            INSERT OR REPLACE INTO task_columns (task_id, column_id)
            VALUES (?, ?)
        """, (task_id, column_id))

        columns = self.col_repo.find_all()
        total = len(columns)
        position = next((c.position for c in columns if c.id == column_id), 1)
        progress = 0 if total < 2 else round((position - 1) / (total - 1) * 100)

        cur.execute("UPDATE tasks SET progress=? WHERE id=?", (progress, task_id))
        if progress == 100:
            cur.execute("UPDATE tasks SET completed_at=CURRENT_TIMESTAMP WHERE id=?",
                        (task_id,))
        self.db.commit()

        self.taskMoved.emit(task_id, progress)