import shutil
from pathlib import Path
from datetime import datetime, timedelta
from models.database import Database
from models.entities import Task, Section, Tag, BoardColumn, Attachment

STORAGE_DIR = Path(__file__).parent.parent / "storage"


class TaskRepository:
    def __init__(self):
        self.db = Database()

    def create(self, task: Task) -> int:
        task.validate()
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO tasks (title, description, section_id, priority, status, progress, deadline, color) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (task.title, task.description, task.section_id, task.priority,
             task.status, task.progress, task.deadline, task.color)
        )
        self.db.commit()
        return cur.lastrowid

    def find_by_id(self, task_id: int) -> Task:
        cur = self.db.cursor()
        row = cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return Task(**dict(row)) if row else None

    def find_all(self) -> list:
        cur = self.db.cursor()
        rows = cur.execute("SELECT * FROM tasks WHERE status='active'").fetchall()
        return [Task(**dict(r)) for r in rows]

    def find_by_section(self, section_id) -> list:
        cur = self.db.cursor()
        if section_id is None:
            rows = cur.execute(
                "SELECT * FROM tasks WHERE section_id IS NULL AND status='active'"
            ).fetchall()
        else:
            rows = cur.execute(
                "SELECT * FROM tasks WHERE section_id=? AND status='active'",
                (section_id,)
            ).fetchall()
        return [Task(**dict(r)) for r in rows]

    def find_archived(self) -> list:
        cur = self.db.cursor()
        rows = cur.execute("SELECT * FROM tasks WHERE status='archived'").fetchall()
        return [Task(**dict(r)) for r in rows]

    def update(self, task: Task):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE tasks SET title=?, description=?, section_id=?, priority=?, "
            "status=?, progress=?, deadline=?, color=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (task.title, task.description, task.section_id, task.priority,
             task.status, task.progress, task.deadline, task.color, task.id)
        )
        self.db.commit()

    def update_progress(self, task_id: int, progress: int):
        cur = self.db.cursor()
        if progress == 100:
            cur.execute(
                "UPDATE tasks SET progress=?, completed_at=CURRENT_TIMESTAMP WHERE id=?",
                (progress, task_id)
            )
        else:
            cur.execute("UPDATE tasks SET progress=? WHERE id=?", (progress, task_id))
        self.db.commit()

    def archive(self, task_id: int):
        cur = self.db.cursor()
        cur.execute("UPDATE tasks SET status='archived' WHERE id=?", (task_id,))
        self.db.commit()

    def restore(self, task_id: int):
        cur = self.db.cursor()
        cur.execute("UPDATE tasks SET status='active' WHERE id=?", (task_id,))
        self.db.commit()

    def delete(self, task_id: int):
        cur = self.db.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.db.commit()


class TaskRepositoryExtended(TaskRepository):
    def find_by_filter(self, criteria: dict) -> list:
        cur = self.db.cursor()
        sql = "SELECT DISTINCT t.* FROM tasks t"
        params = []
        where = ["t.status='active'"]

        if criteria.get("tag_id"):
            sql += " JOIN task_tags tt ON t.id = tt.task_id"
            where.append("tt.tag_id = ?")
            params.append(criteria["tag_id"])

        if criteria.get("title"):
            where.append("LOWER(t.title) LIKE ?")
            params.append(f"%{criteria['title'].lower()}%")

        if criteria.get("priority"):
            where.append("t.priority = ?")
            params.append(criteria["priority"])

        if criteria.get("section_id"):
            where.append("t.section_id = ?")
            params.append(criteria["section_id"])

        if criteria.get("date_from"):
            where.append("t.deadline >= ?")
            params.append(criteria["date_from"])

        if criteria.get("date_to"):
            where.append("t.deadline <= ?")
            params.append(criteria["date_to"])

        sql += " WHERE " + " AND ".join(where)
        rows = cur.execute(sql, params).fetchall()
        return [Task(**dict(r)) for r in rows]

    def bulk_archive(self, ids: list):
        cur = self.db.cursor()
        placeholders = ",".join("?" * len(ids))
        cur.execute(f"UPDATE tasks SET status='archived' WHERE id IN ({placeholders})", ids)
        self.db.commit()

    def bulk_delete(self, ids: list):
        cur = self.db.cursor()
        placeholders = ",".join("?" * len(ids))
        cur.execute(f"DELETE FROM tasks WHERE id IN ({placeholders})", ids)
        self.db.commit()

    def get_upcoming(self, minutes: int = 5) -> list:
        cur = self.db.cursor()
        now = datetime.now()
        soon = now + timedelta(minutes=minutes)
        rows = cur.execute(
            "SELECT * FROM tasks WHERE status!='archived' AND progress<100 "
            "AND deadline IS NOT NULL "
            "AND deadline BETWEEN ? AND ?",
            (now.strftime("%Y-%m-%d %H:%M:%S"), soon.strftime("%Y-%m-%d %H:%M:%S"))
        ).fetchall()
        return [Task(**dict(r)) for r in rows]


class SectionRepository:
    def __init__(self):
        self.db = Database()

    def create(self, section: Section) -> int:
        section.validate()
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO sections (name, color) VALUES (?, ?)",
            (section.name, section.color)
        )
        self.db.commit()
        return cur.lastrowid

    def find_all(self) -> list:
        cur = self.db.cursor()
        rows = cur.execute("SELECT * FROM sections WHERE status='active'").fetchall()
        return [Section(**dict(r)) for r in rows]

    def delete_with_tasks(self, section_id: int):
        cur = self.db.cursor()
        cur.execute("DELETE FROM tasks WHERE section_id=?", (section_id,))
        cur.execute("DELETE FROM sections WHERE id=?", (section_id,))
        self.db.commit()

    def delete_only(self, section_id: int):
        cur = self.db.cursor()
        cur.execute("UPDATE tasks SET section_id=NULL WHERE section_id=?", (section_id,))
        cur.execute("DELETE FROM sections WHERE id=?", (section_id,))
        self.db.commit()


class TagRepository:
    def __init__(self):
        self.db = Database()

    def find_all(self) -> list:
        cur = self.db.cursor()
        rows = cur.execute("SELECT * FROM tags").fetchall()
        return [Tag(**dict(r)) for r in rows]

    def create(self, name: str, color: str = "#cccccc") -> int:
        cur = self.db.cursor()
        cur.execute("INSERT OR IGNORE INTO tags (name, color) VALUES (?, ?)", (name, color))
        self.db.commit()
        return cur.lastrowid

    def link_to_task(self, task_id: int, tag_id: int):
        cur = self.db.cursor()
        cur.execute("INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                    (task_id, tag_id))
        self.db.commit()

    def get_task_tags(self, task_id: int) -> list:
        cur = self.db.cursor()
        rows = cur.execute("""
            SELECT t.* FROM tags t
            JOIN task_tags tt ON tt.tag_id = t.id
            WHERE tt.task_id = ?
        """, (task_id,)).fetchall()
        return [Tag(**dict(r)) for r in rows]


class BoardColumnRepository:
    def __init__(self):
        self.db = Database()

    def find_all(self) -> list:
        cur = self.db.cursor()
        rows = cur.execute("SELECT * FROM board_columns ORDER BY position").fetchall()
        return [BoardColumn(**dict(r)) for r in rows]

    def create(self, name: str, color: str = "#e0e0e0") -> int:
        cur = self.db.cursor()
        pos = cur.execute("SELECT COALESCE(MAX(position), 0) + 1 FROM board_columns").fetchone()[0]
        cur.execute("INSERT INTO board_columns (name, position, color) VALUES (?, ?, ?)",
                    (name, pos, color))
        self.db.commit()
        return cur.lastrowid

    def rename(self, column_id: int, new_name: str):
        cur = self.db.cursor()
        cur.execute("UPDATE board_columns SET name=? WHERE id=?", (new_name, column_id))
        self.db.commit()

    def delete(self, column_id: int):
        cur = self.db.cursor()
        cur.execute("DELETE FROM board_columns WHERE id=?", (column_id,))
        self.db.commit()

    def count(self) -> int:
        cur = self.db.cursor()
        return cur.execute("SELECT COUNT(*) FROM board_columns").fetchone()[0]


class AttachmentRepository:
    def __init__(self):
        self.db = Database()

    def attach(self, task_id: int, file_name: str, file_path: str):
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO attachments (task_id, file_name, file_path) VALUES (?, ?, ?)",
            (task_id, file_name, file_path)
        )
        self.db.commit()

    def find_by_task(self, task_id: int) -> list:
        cur = self.db.cursor()
        rows = cur.execute("SELECT * FROM attachments WHERE task_id=?", (task_id,)).fetchall()
        return [Attachment(**dict(r)) for r in rows]

    def attach_file(self, task_id: int, source_path: str) -> str:
        STORAGE_DIR.mkdir(exist_ok=True)
        src = Path(source_path)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_name = f"{task_id}_{stamp}_{src.name}"
        dest = STORAGE_DIR / dest_name
        shutil.copy2(src, dest)
        self.attach(task_id, src.name, str(dest))
        return str(dest)


class TimeLogRepository:
    def __init__(self):
        self.db = Database()

    def start(self, task_id: int) -> int:
        cur = self.db.cursor()
        cur.execute("INSERT INTO time_logs (task_id, started_at) VALUES (?, CURRENT_TIMESTAMP)",
                    (task_id,))
        self.db.commit()
        return cur.lastrowid

    def get_total_by_section(self) -> list:
        cur = self.db.cursor()
        rows = cur.execute("""
            SELECT s.name AS name, COALESCE(SUM(tl.duration_sec), 0) AS total
            FROM sections s
            LEFT JOIN tasks t ON t.section_id = s.id
            LEFT JOIN time_logs tl ON tl.task_id = t.id
            GROUP BY s.id
        """).fetchall()
        return [dict(r) for r in rows]

    def get_time_by_column(self, period: str = "all") -> list:
        """Сколько времени задачи провели в каждой колонке."""
        cur = self.db.cursor()
        sql = """
            SELECT 
                bc.name AS column_name,
                bc.color AS color,
                bc.position AS position,
                COALESCE(SUM(tl.duration_sec), 0) AS total_sec,
                COUNT(DISTINCT tl.task_id) AS tasks_count
            FROM board_columns bc
            LEFT JOIN time_logs tl ON tl.column_id = bc.id
        """
        params = []
        if period != "all":
            days = {"day": 1, "week": 7, "month": 30}.get(period, 1)
            sql += " WHERE tl.started_at >= date('now', ?)"
            params.append(f"-{days} days")
        sql += " GROUP BY bc.id ORDER BY bc.position"
        rows = cur.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_done_count(self, period: str = "all") -> int:
        cur = self.db.cursor()
        if period == "all":
            return cur.execute("SELECT COUNT(*) FROM tasks WHERE progress=100").fetchone()[0]
        days = {"day": 1, "week": 7, "month": 30}.get(period, 1)
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return cur.execute(
            "SELECT COUNT(*) FROM tasks WHERE progress=100 AND updated_at >= ?",
            (since,)
        ).fetchone()[0]


class SettingsRepository:
    def __init__(self):
        self.db = Database()

    def get(self, key: str, default=None):
        cur = self.db.cursor()
        row = cur.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default

    def set(self, key: str, value: str):
        cur = self.db.cursor()
        cur.execute("INSERT OR REPLACE INTO settings (key, value, updated_at) "
                    "VALUES (?, ?, CURRENT_TIMESTAMP)", (key, value))
        self.db.commit()


class NotificationsLogRepository:
    def __init__(self):
        self.db = Database()

    def log(self, task_id: int):
        cur = self.db.cursor()
        cur.execute("INSERT INTO notifications_log (task_id) VALUES (?)", (task_id,))
        self.db.commit()