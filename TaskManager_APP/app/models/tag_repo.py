from app.db.connection import get_connection, transactional
from app.models.entities import Tag, ValidationError
from app.config import MAX_TAG_LEN

class TagRepo:
    @staticmethod
    @transactional
    def get_all(conn):
        rows = conn.execute("SELECT * FROM tags ORDER BY name ASC").fetchall()
        return [Tag(**dict(r)) for r in rows]

    @staticmethod
    @transactional
    def create(conn, name: str) -> int:
        name = name.strip()
        if not name:
            raise ValidationError("Имя тега не может быть пустым.")
        if len(name) > MAX_TAG_LEN:
            raise ValidationError(f"Имя тега не может превышать {MAX_TAG_LEN} символов.")
        
        try:
            cur = conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
            return cur.lastrowid
        except Exception:
            raise ValidationError("Тег с таким именем уже существует.")

    @staticmethod
    @transactional
    def add_to_task(conn, task_id: int, tag_id: int):
        conn.execute("INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)", (task_id, tag_id))

    @staticmethod
    @transactional
    def remove_from_task(conn, task_id: int, tag_id: int):
        conn.execute("DELETE FROM task_tags WHERE task_id = ? AND tag_id = ?", (task_id, tag_id))
        
    @staticmethod
    @transactional
    def get_for_task(conn, task_id: int):
        rows = conn.execute(
            "SELECT t.* FROM tags t JOIN task_tags tt ON t.id = tt.tag_id WHERE tt.task_id = ?", (task_id,)
        ).fetchall()
        return [Tag(**dict(r)) for r in rows]