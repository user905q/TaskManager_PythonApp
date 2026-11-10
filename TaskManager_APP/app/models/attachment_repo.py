import os
import shutil
import uuid
from pathlib import Path
from app.db.connection import get_connection, transactional
from app.models.entities import Attachment, ValidationError
from app.config import MAX_ATTACHMENTS, STORAGE_DIR

class AttachmentRepo:
    @staticmethod
    @transactional
    def add_attachment(conn, task_id: int, source_path: str) -> int:
        # 1. Проверка лимита
        count = conn.execute("SELECT COUNT(*) FROM attachments WHERE task_id = ?", (task_id,)).fetchone()[0]
        if count >= MAX_ATTACHMENTS:
            raise ValidationError(f"Достигнут лимит вложений ({MAX_ATTACHMENTS}).")

        src = Path(source_path)
        if not src.exists():
            raise ValidationError("Файл не найден.")

        # 2. Проверка места (грубо: размер файла + 10МБ запас)
        stat = os.stat(src)
        free_space = shutil.disk_usage(STORAGE_DIR).free
        if free_space < stat.st_size + (10 * 1024 * 1024):
            raise ValidationError("Недостаточно места на диске.")

        # 3. Копирование с уникальным именем
        ext = src.suffix
        stored_name = f"{uuid.uuid4().hex}{ext}"
        dest = STORAGE_DIR / stored_name
        shutil.copy2(src, dest)

        # 4. Запись в БД
        try:
            cur = conn.execute(
                "INSERT INTO attachments (task_id, original_name, stored_name, size) VALUES (?, ?, ?, ?)",
                (task_id, src.name, stored_name, stat.st_size)
            )
            return cur.lastrowid
        except Exception:
            dest.unlink(missing_ok=True) # Откат файла при ошибке БД
            raise

    @staticmethod
    @transactional
    def get_for_task(conn, task_id: int):
        rows = conn.execute("SELECT * FROM attachments WHERE task_id = ?", (task_id,)).fetchall()
        return [Attachment(**dict(r)) for r in rows]