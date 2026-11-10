from app.db.connection import get_connection, transactional
from datetime import datetime, timedelta

class NotificationRepo:
    @staticmethod
    @transactional
    def get_upcoming_deadlines(conn):
        # Ищем задачи, до дедлайна которых осталось < 30 минут, и уведомление еще не отправлялось
        now = datetime.now()
        soon = now + timedelta(minutes=30)
        
        rows = conn.execute("""
            SELECT t.id, t.title, t.deadline 
            FROM tasks t
            WHERE t.is_archived = 0 
              AND t.deadline BETWEEN ? AND ?
              AND NOT EXISTS (
                  SELECT 1 FROM notifications_log nl 
                  WHERE nl.task_id = t.id AND nl.type = 'deadline'
              )
        """, (now.isoformat(), soon.isoformat())).fetchall()
        return rows

    @staticmethod
    @transactional
    def log_notification(conn, task_id: int, type_: str):
        conn.execute("INSERT INTO notifications_log (task_id, type) VALUES (?, ?)", (task_id, type_))