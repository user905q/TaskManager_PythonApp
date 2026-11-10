from datetime import datetime
from app.db.connection import get_connection, transactional

class TimeLogRepo:
    @staticmethod
    def process_column_change(conn, task_id: int, new_column_position: int, total_columns: int):
        from datetime import datetime
        now = datetime.now().isoformat()
        
        # 1. Всегда закрываем предыдущую открытую сессию (если есть)
        active = conn.execute(
            "SELECT id, started_at FROM time_logs WHERE task_id = ? AND ended_at IS NULL", (task_id,)
        ).fetchone()
        
        if active:
            start_time = datetime.fromisoformat(active["started_at"])
            duration = int((datetime.now() - start_time).total_seconds())
            # Записываем, даже если прошло 1 секунда
            conn.execute(
                "UPDATE time_logs SET ended_at = ?, duration_sec = ? WHERE id = ?",
                (now, duration, active["id"])
            )

        # 2. Открываем новую сессию, ТОЛЬКО если задача не в последней колонке
        if new_column_position < total_columns - 1:
            conn.execute(
                "INSERT INTO time_logs (task_id, started_at) VALUES (?, ?)",
                (task_id, now)
            )

    @staticmethod
    @transactional
    def close_active_session(conn, task_id: int):
        # Вызывается при архивации/удалении задачи
        now = datetime.now().isoformat()
        active = conn.execute(
            "SELECT id, started_at FROM time_logs WHERE task_id = ? AND ended_at IS NULL", (task_id,)
        ).fetchone()
        if active:
            start_time = datetime.fromisoformat(active["started_at"])
            duration = int((datetime.now() - start_time).total_seconds())
            conn.execute(
                "UPDATE time_logs SET ended_at = ?, duration_sec = ? WHERE id = ?",
                (now, duration, active["id"])
            )