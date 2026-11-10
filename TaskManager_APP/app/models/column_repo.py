from app.models.entities import ValidationError
import math
from app.db.connection import get_connection, transactional
from app.models.entities import BoardColumn

class ColumnRepo:
    @staticmethod
    @transactional
    def get_all(conn):
        rows = conn.execute("SELECT * FROM board_columns ORDER BY position ASC").fetchall()
        return [BoardColumn(**dict(r)) for r in rows]

    @staticmethod
    def calculate_progress(column_position: int, total_columns: int) -> int:
        if total_columns <= 1:
            return 100
        if column_position <= 1:
            return 0
        return math.ceil(((column_position - 1) / (total_columns - 1)) * 100)

    # @staticmethod
    # def move_task(task_id: int, new_column_id: int):
    #     with get_connection() as conn:
    #         conn.execute("BEGIN IMMEDIATE")
    #         try:
    #             conn.execute("UPDATE task_columns SET column_id = ? WHERE task_id = ?", (new_column_id, task_id))
                
    #             col_info = conn.execute(
    #                 "SELECT position FROM board_columns WHERE id = ?", (new_column_id,)
    #             ).fetchone()
    #             total_cols = conn.execute("SELECT COUNT(*) FROM board_columns").fetchone()[0]
                
    #             if col_info:
    #                 from app.models.timelog_repo import TimeLogRepo
    #                 TimeLogRepo.process_column_change(conn, task_id, col_info["position"], total_cols)
                
    #             conn.commit()
    #         except Exception as e:
    #             conn.rollback()
    #             raise e

    @staticmethod
    def move_task(task_id: int, new_column_id: int):
        with get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute("UPDATE task_columns SET column_id = ? WHERE task_id = ?", (new_column_id, task_id))
                
                # ОБНОВЛЯЕМ ВРЕМЯ ПОСЛЕДНЕГО ИЗМЕНЕНИЯ
                from datetime import datetime
                now = datetime.now().isoformat()
                conn.execute("UPDATE tasks SET updated_at = ? WHERE id = ?", (now, task_id))
                
                col_info = conn.execute(
                    "SELECT position FROM board_columns WHERE id = ?", (new_column_id,)
                ).fetchone()
                total_cols = conn.execute("SELECT COUNT(*) FROM board_columns").fetchone()[0]
                
                if col_info:
                    from app.models.timelog_repo import TimeLogRepo
                    TimeLogRepo.process_column_change(conn, task_id, col_info["position"], total_cols)
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    @staticmethod
    @transactional
    def create_column(conn, name: str) -> int:
        count = conn.execute("SELECT COUNT(*) FROM board_columns").fetchone()[0]
        if count >= 10:
            raise ValidationError("Достигнут лимит колонок (10).")
        
        max_pos = conn.execute("SELECT MAX(position) FROM board_columns").fetchone()[0] or 0
        cur = conn.execute("INSERT INTO board_columns (name, position) VALUES (?, ?)", (name, max_pos + 1))
        return cur.lastrowid

    @staticmethod
    @transactional
    def rename_column(conn, column_id: int, new_name: str):
        if not new_name.strip():
            raise ValidationError("Название колонки не может быть пустым.")
        conn.execute("UPDATE board_columns SET name = ? WHERE id = ?", (new_name, column_id))

    @staticmethod
    @transactional
    def delete_column(conn, column_id: int):
        count = conn.execute("SELECT COUNT(*) FROM board_columns").fetchone()[0]
        if count <= 1:
            raise ValidationError("Должна остаться хотя бы одна колонка.")
            
        # Находим ID первой колонки, чтобы перекинуть туда задачи
        first_col = conn.execute("SELECT id FROM board_columns WHERE id != ? ORDER BY position ASC LIMIT 1", (column_id,)).fetchone()
        
        if first_col:
            # Переносим задачи из удаляемой колонки в первую
            conn.execute("UPDATE task_columns SET column_id = ? WHERE column_id = ?", (first_col["id"], column_id))
            
        conn.execute("DELETE FROM board_columns WHERE id = ?", (column_id,))