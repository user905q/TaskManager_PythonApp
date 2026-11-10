from app.db.connection import get_connection, transactional
from app.models.entities import Task, ValidationError
from app.config import MAX_TITLE_LEN
from datetime import datetime

class TaskRepo:
    @staticmethod
    def _validate(task: Task):
        if not task.title or not task.title.strip():
            raise ValidationError("Название задачи не может быть пустым.")
        if len(task.title) > MAX_TITLE_LEN:
            raise ValidationError(f"Название не может превышать {MAX_TITLE_LEN} символов.")
        
        if task.deadline:
            from datetime import datetime
            # Если дедлайн пришел строкой - конвертируем
            if isinstance(task.deadline, str):
                try:
                    deadline_dt = datetime.fromisoformat(task.deadline)
                except ValueError:
                    raise ValidationError("Неверный формат даты.")
            else:
                deadline_dt = task.deadline
                
            if deadline_dt < datetime.now():
                raise ValidationError("Дата дедлайна не может быть в прошлом.")

    @staticmethod
    @transactional
    def create(conn, task: Task) -> int:
        TaskRepo._validate(task)
        
        # Если раздел не указан, привязываем к системному
        section_id = task.section_id
        if not section_id:
            sys_row = conn.execute("SELECT id FROM sections WHERE is_system = 1 LIMIT 1").fetchone()
            if sys_row:
                section_id = sys_row["id"]

        cur = conn.execute(
            "INSERT INTO tasks (title, description, section_id, color, deadline) VALUES (?, ?, ?, ?, ?)",
            (task.title.strip(), task.description, section_id, task.color, task.deadline)
        )
        task_id = cur.lastrowid
        
        # --- ПРАВИЛЬНЫЙ БЛОК ---
        first_col = conn.execute("SELECT id FROM board_columns ORDER BY position LIMIT 1").fetchone()
        if first_col:
            conn.execute("INSERT INTO task_columns (task_id, column_id) VALUES (?, ?)", (task_id, first_col["id"]))
            # Запускаем таймер сразу при создании!
            from app.models.timelog_repo import TimeLogRepo
            TimeLogRepo.process_column_change(conn, task_id, 0, 1)
            
        return task_id

    @staticmethod
    @transactional
    def get_all_active(conn, limit: int = 50, offset: int = 0):
        # Автосортировка: по дедлайну (NULL в конце), затем по названию
        rows = conn.execute(
            """SELECT * FROM tasks WHERE is_archived = 0 
               ORDER BY deadline IS NULL, deadline ASC, title ASC 
               LIMIT ? OFFSET ?""", (limit, offset)
        ).fetchall()
        return [Task(**dict(r)) for r in rows]

    @staticmethod
    @transactional
    def archive(conn, task_id: int):
        conn.execute("UPDATE tasks SET is_archived = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))

    @staticmethod
    @transactional
    def delete(conn, task_id: int):
        # Получаем список файлов для удаления
        attachments = conn.execute("SELECT stored_name FROM attachments WHERE task_id = ?", (task_id,)).fetchall()
        from app.config import STORAGE_DIR
        for att in attachments:
            filepath = STORAGE_DIR / att["stored_name"]
            if filepath.exists():
                filepath.unlink() # Удаляем физический файл
                
        # Удаляем задачу (связи удалятся каскадно)
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    @staticmethod
    @transactional
    def get_by_id(conn, task_id: int):
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return Task(**dict(row)) if row else None

    @staticmethod
    @transactional
    def update(conn, task_id: int, title: str, description: str, section_id: int, deadline):
        TaskRepo._validate(Task(title=title, deadline=deadline))
        conn.execute("""
            UPDATE tasks 
            SET title = ?, description = ?, section_id = ?, deadline = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (title, description, section_id, deadline, task_id))