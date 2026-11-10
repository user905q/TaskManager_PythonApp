from app.db.connection import get_connection, transactional
from datetime import datetime

class StatsRepo:
    @staticmethod
    @transactional
    def get_tasks_by_column(conn):
        rows = conn.execute("""
            SELECT bc.name, COUNT(tc.task_id) as count
            FROM board_columns bc
            LEFT JOIN task_columns tc ON bc.id = tc.column_id
            LEFT JOIN tasks t ON tc.task_id = t.id AND t.is_archived = 0
            GROUP BY bc.id 
            ORDER BY bc.position ASC
        """).fetchall()
        # Исключаем колонки с 0 задач для круговой диаграммы, как ты просил
        return {r["name"]: r["count"] for r in rows if r["count"] > 0}

    @staticmethod
    @transactional
    def get_completed_by_days(conn, days: int):
        # Возвращает словарь { 'YYYY-MM-DD': count } за последние N дней
        from datetime import timedelta
        result = {}
        now = datetime.now()
        for i in range(days):
            date_str = (now - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            row = conn.execute("""
                SELECT COUNT(t.id) FROM tasks t
                JOIN task_columns tc ON t.id = tc.task_id
                JOIN board_columns bc ON tc.column_id = bc.id
                WHERE bc.position = (SELECT MAX(position) FROM board_columns)
                  AND t.is_archived = 0
                  AND DATE(t.updated_at) = ?
            """, (date_str,)).fetchone()
            result[date_str] = row[0]
        return result

    @staticmethod
    @transactional
    def get_completed_by_sections(conn, days: int):
        # Сколько выполнено задач в каждом разделе за N дней
        from datetime import timedelta
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute("""
            SELECT s.name, COUNT(t.id) as count
            FROM sections s
            LEFT JOIN tasks t ON s.id = t.section_id 
                AND t.is_archived = 0 
                AND t.updated_at >= ?
                AND t.id IN (
                    SELECT tc.task_id FROM task_columns tc 
                    JOIN board_columns bc ON tc.column_id = bc.id 
                    WHERE bc.position = (SELECT MAX(position) FROM board_columns)
                )
            GROUP BY s.id
        """, (start_date,)).fetchall()
        return {r["name"]: r["count"] for r in rows if r["count"] > 0}

    @staticmethod
    @transactional
    def get_time_spent(conn):
        from datetime import datetime
        now = datetime.now()
        
        rows = conn.execute("""
            SELECT t.id, t.title, t.created_at, t.updated_at,
                   s.name as section_name,
                   (SELECT bc.position FROM task_columns tc 
                    JOIN board_columns bc ON tc.column_id = bc.id 
                    WHERE tc.task_id = t.id) as col_pos,
                   (SELECT MAX(position) FROM board_columns) as max_pos
            FROM tasks t
            LEFT JOIN sections s ON t.section_id = s.id
            WHERE t.is_archived = 0
        """).fetchall()

        tasks_time = {}
        sections_time = {}

        for r in rows:
            # Берем время из базы
            c_str = str(r["created_at"]).replace("T", " ").split(".")[0]
            try:
                created = datetime.strptime(c_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                created = now

            # Если задача в последней колонке (Выполнено) - берем updated_at
            if r["col_pos"] == r["max_pos"]:
                u_str = str(r["updated_at"]).replace("T", " ").split(".")[0]
                try:
                    end = datetime.strptime(u_str, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    end = now
            else:
                end = now
            
            # Считаем разницу
            sec = int((end - created).total_seconds())
            
            # Если разница отрицательная (из-за кривой даты), ставим 0
            if sec < 0:
                sec = 0
                
            tasks_time[r["title"]] = sec
            sec_name = r["section_name"] or "Задачи без раздела"
            sections_time[sec_name] = sections_time.get(sec_name, 0) + sec

        return tasks_time, sections_time