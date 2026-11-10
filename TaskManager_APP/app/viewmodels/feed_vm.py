from app.viewmodels.base import BaseViewModel
from app.db.connection import get_connection
from app.models.entities import Task

class FeedViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()

    def get_filtered_tasks(self, search_text: str = "", section_id: int = None, limit: int = 50, offset: int = 0):
        try:
            with get_connection() as conn:
                query = """
                    SELECT t.* FROM tasks t
                    WHERE t.is_archived = 0
                """
                params = []

                if search_text:
                    query += " AND t.title LIKE ? ESCAPE '\\'"
                    # Экранирование спецсимволов
                    safe_text = search_text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                    params.append(f"%{safe_text}%")

                if section_id:
                    query += " AND t.section_id = ?"
                    params.append(section_id)

                # Сортировка: раздел (чтобы шли друг за другом), затем дедлайн, затем название
                query += " ORDER BY t.section_id IS NULL, t.section_id ASC, t.deadline IS NULL, t.deadline ASC, t.title ASC"
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                rows = conn.execute(query, params).fetchall()
                return [Task(**dict(r)) for r in rows]
        except Exception as e:
            self.handle_exception(e)
            return []