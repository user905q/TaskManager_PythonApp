from app.viewmodels.base import BaseViewModel
from app.db.connection import get_connection
from app.models.column_repo import ColumnRepo
from app.models.task_repo import TaskRepo
from app.models.section_repo import SectionRepo
from app.models.entities import Task, Section

class BoardViewModel(BaseViewModel):
    def __init__(self):
        super().__init__()

    def get_board_data(self):
        """Собирает данные для обеих зон Канбан-доски"""
        try:
            with get_connection() as conn:
                # 1. Получаем колонки
                cols = conn.execute("SELECT * FROM board_columns ORDER BY position").fetchall()
                total_cols = len(cols)
                
                # 2. Получаем задачи для верхней зоны (сортируем по дедлайну, потом по названию)
                tasks_raw = conn.execute(
                    "SELECT * FROM tasks WHERE is_archived = 0 ORDER BY deadline IS NULL, deadline ASC, title ASC"
                ).fetchall()
                
                # 3. Получаем разделы для нижней зоны
                sections_raw = conn.execute("SELECT * FROM sections WHERE is_archived = 0").fetchall()

                # Собираем задачи в колонки
                columns_data = []
                for c in cols:
                    col_tasks = []
                    for t in tasks_raw:
                        # Ищем, в какой колонке задача
                        tc = conn.execute("SELECT column_id FROM task_columns WHERE task_id = ?", (t["id"],)).fetchone()
                        if tc and tc["column_id"] == c["id"]:
                            # Вычисляем прогресс для задачи
                            progress = ColumnRepo.calculate_progress(c["position"] + 1, total_cols)
                            col_tasks.append({
                                "task": Task(**dict(t)),
                                "progress": progress
                            })
                    columns_data.append({
                        "column": dict(c),
                        "tasks": col_tasks
                    })

                # Собираем данные для разделов (нижняя зона)
                sections_data = []
                for s in sections_raw:
                    # Получаем задачи этого раздела
                    s_tasks = [t for t in tasks_raw if t["section_id"] == s["id"]]
                    
                    # Считаем прогресс раздела (среднее арифметическое прогрессов задач)
                    total_progress = 0
                    tasks_with_progress = []
                    for st in s_tasks:
                        tc = conn.execute("SELECT column_id FROM task_columns WHERE task_id = ?", (st["id"],)).fetchone()
                        prog = 0
                        if tc:
                            col_pos = next((c["position"] for c in cols if c["id"] == tc["column_id"]), 1)
                            prog = ColumnRepo.calculate_progress(col_pos + 1, total_cols)
                        total_progress += prog
                        tasks_with_progress.append({"task": Task(**dict(st)), "progress": prog})
                    
                    # Округление вверх (math.ceil)
                    import math
                    sec_prog = math.ceil(total_progress / len(s_tasks)) if s_tasks else 0
                    
                    # Сортировка задач в разделе: по прогрессу (возр), затем по id (возр)
                    tasks_with_progress.sort(key=lambda x: (x["progress"], x["task"].id))

                    sections_data.append({
                        "section": Section(**dict(s)),
                        "progress": sec_prog,
                        "tasks": tasks_with_progress
                    })
                
                # Сортировка разделов: по прогрессу (возр), затем по id (возр)
                sections_data.sort(key=lambda x: (x["progress"], x["section"].id))

                return columns_data, sections_data
        except Exception as e:
            self.handle_exception(e)
            return [], []

    def move_task(self, task_id: int, new_column_id: int):
        try:
            ColumnRepo.move_task(task_id, new_column_id)
            self.data_changed.emit("board") # Сигнал: обновить доску
        except Exception as e:
            self.handle_exception(e)