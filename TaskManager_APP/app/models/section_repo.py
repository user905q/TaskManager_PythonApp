from app.db.connection import get_connection, transactional
from app.models.entities import Section, ValidationError
from app.config import MAX_TITLE_LEN, SYSTEM_SECTION_NAME

class SectionRepo:
    @staticmethod
    def _validate(section: Section):
        if not section.name or not section.name.strip():
            raise ValidationError("Название раздела не может быть пустым.")
        if len(section.name) > MAX_TITLE_LEN:
            raise ValidationError(f"Название не может превышать {MAX_TITLE_LEN} символов.")

    @staticmethod
    @transactional
    def create(conn, section: Section) -> int:
        SectionRepo._validate(section)
        cur = conn.execute(
            "INSERT INTO sections (name, color) VALUES (?, ?)",
            (section.name.strip(), section.color)
        )
        return cur.lastrowid

    @staticmethod
    @transactional
    def update(conn, section_id: int, name: str, color: str):
        if not name or not name.strip():
            raise ValidationError("Название раздела не может быть пустым.")
        if len(name) > MAX_TITLE_LEN:
            raise ValidationError(f"Название не может превышать {MAX_TITLE_LEN} символов.")
        conn.execute("UPDATE sections SET name = ?, color = ? WHERE id = ?", (name.strip(), color, section_id))

    @staticmethod
    @transactional
    def get_all_active(conn):
        # По возрастанию прогресса (пока заглушка, так как прогресс считается в column_repo)
        rows = conn.execute("SELECT * FROM sections WHERE is_archived = 0 ORDER BY id ASC").fetchall()
        return [Section(**dict(r)) for r in rows]

    @staticmethod
    @transactional
    def delete_section_only(conn, section_id: int):
        # Удаляем только раздел, задачи переходят в системный
        sys_row = conn.execute("SELECT id FROM sections WHERE is_system = 1 LIMIT 1").fetchone()
        if not sys_row:
            raise ValidationError("Системный раздел не найден.")
        sys_id = sys_row["id"]
        
        conn.execute("UPDATE tasks SET section_id = ? WHERE section_id = ?", (sys_id, section_id))
        conn.execute("DELETE FROM sections WHERE id = ? AND is_system = 0", (section_id,))

    @staticmethod
    @transactional
    def delete_with_tasks(conn, section_id: int):
        # Явно удаляем все задачи этого раздела (вместе с их связями)
        conn.execute("DELETE FROM tasks WHERE section_id = ?", (section_id,))
        # Удаляем сам раздел
        conn.execute("DELETE FROM sections WHERE id = ? AND is_system = 0", (section_id,))

    @staticmethod
    @transactional
    def archive_section(conn, section_id: int):
        conn.execute("UPDATE sections SET is_archived = 1 WHERE id = ? AND is_system = 0", (section_id,))
        conn.execute("UPDATE tasks SET is_archived = 1 WHERE section_id = ?", (section_id,))