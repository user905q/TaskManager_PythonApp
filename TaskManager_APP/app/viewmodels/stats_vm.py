from app.viewmodels.base import BaseViewModel
from app.models.stats_repo import StatsRepo
from app.db.connection import get_connection
from app.models.section_repo import SectionRepo

class StatsViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()

    def get_stats_data(self, days: int = 7):
        try:
            tasks_by_column = StatsRepo.get_tasks_by_column()
            completed_by_days = StatsRepo.get_completed_by_days(days)
            completed_by_sections = StatsRepo.get_completed_by_sections(days)
            tasks_time, sections_time = StatsRepo.get_time_spent()
            
            with get_connection() as conn:
                total_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE is_archived = 0").fetchone()[0]
                
                # Считаем "В работе" и "Выполнено" для нижней панели
                in_progress = 0
                done = 0
                cols = conn.execute("""
                    SELECT bc.position, COUNT(tc.task_id) as count
                    FROM board_columns bc
                    LEFT JOIN task_columns tc ON bc.id = tc.column_id
                    LEFT JOIN tasks t ON tc.task_id = t.id AND t.is_archived = 0
                    GROUP BY bc.id ORDER BY bc.position
                """).fetchall()
                
                if cols:
                    counts = [c["count"] for c in cols]
                    if len(counts) >= 3:
                        in_progress = sum(counts[1:-1])
                        done = counts[-1]
                    elif len(counts) == 2:
                        done = counts[-1]

                total_time = sum(tasks_time.values())
                
                sections = SectionRepo.get_all_active()
                sections_list = [{"id": None, "name": "Все разделы"}] + [{"id": s.id, "name": s.name} for s in sections if not s.is_system]
            
            return {
                "tasks_by_column": tasks_by_column,
                "completed_by_days": completed_by_days,
                "completed_by_sections": completed_by_sections,
                "tasks_time": tasks_time,
                "sections_time": sections_time,
                "sections_list": sections_list,
                "summary": {
                    "total": total_tasks, "in_progress": in_progress, 
                    "done": done, "time_sec": total_time
                }
            }
        except Exception as e:
            self.handle_exception(e)
            return {}