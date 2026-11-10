from app.db.connection import get_connection, transactional
from app.models.entities import Task, Section

class ArchiveRepo:
    @staticmethod
    @transactional
    def get_archived_sections(conn):
        rows = conn.execute("SELECT * FROM sections WHERE is_archived = 1").fetchall()
        return [Section(**dict(r)) for r in rows]

    @staticmethod
    @transactional
    def get_archived_tasks(conn):
        rows = conn.execute("SELECT * FROM tasks WHERE is_archived = 1").fetchall()
        return [Task(**dict(r)) for r in rows]

    @staticmethod
    @transactional
    def archive_section_with_tasks(conn, section_id: int):
        conn.execute("UPDATE sections SET is_archived = 1 WHERE id = ? AND is_system = 0", (section_id,))
        conn.execute("UPDATE tasks SET is_archived = 1 WHERE section_id = ?", (section_id,))
        
    @staticmethod
    @transactional
    def restore_task(conn, task_id: int):
        # Восстанавливаем задачу
        conn.execute("UPDATE tasks SET is_archived = 0 WHERE id = ?", (task_id,))
        
        # Проверяем, существует ли её раздел
        task = conn.execute("SELECT section_id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if task and task["section_id"]:
            sec = conn.execute("SELECT is_archived, is_system FROM sections WHERE id = ?", (task["section_id"],)).fetchone()
            if not sec or sec["is_archived"]:
                # Если раздела нет или он архивный — кидаем в системный
                sys_row = conn.execute("SELECT id FROM sections WHERE is_system = 1").fetchone()
                if sys_row:
                    conn.execute("UPDATE tasks SET section_id = ? WHERE id = ?", (sys_row["id"], task_id))

    @staticmethod
    @transactional
    def restore_section(conn, section_id: int):
        conn.execute("UPDATE sections SET is_archived = 0 WHERE id = ?", (section_id,))
        conn.execute("UPDATE tasks SET is_archived = 0 WHERE section_id = ?", (section_id,))