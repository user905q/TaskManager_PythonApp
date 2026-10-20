import logging
from pathlib import Path
from app.db.connection import get_connection, transactional
from app.config import DEFAULT_COLUMNS, DEFAULT_TAGS, SYSTEM_SECTION_NAME

def init_db():
    conn = get_connection()
    try:
        # Чтение схемы
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

        # Проверка, нужно ли вставить предустановленные данные
        cur = conn.execute("SELECT COUNT(*) FROM board_columns")
        if cur.fetchone()[0] == 0:
            _insert_defaults(conn)
            conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f"Migration error: {e}")
        raise
    finally:
        conn.close()


def _insert_defaults(conn):
    # 1. Колонки
    for i, col_name in enumerate(DEFAULT_COLUMNS):
        conn.execute("INSERT INTO board_columns (name, position) VALUES (?, ?)", (col_name, i))
    
    # 2. Теги
    for tag in DEFAULT_TAGS:
        conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
    
    # 3. Системный раздел
    conn.execute(
        "INSERT INTO sections (name, color, is_system) VALUES (?, ?, ?)",
        (SYSTEM_SECTION_NAME, "#9CA3AF", 1)
    )