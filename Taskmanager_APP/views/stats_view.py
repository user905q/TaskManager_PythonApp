from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QRadioButton, QLabel, QGroupBox, QButtonGroup
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from viewmodels.stats_vm import StatsViewModel


class StatsView(QWidget):
    def __init__(self):
        super().__init__()
        self.vm = StatsViewModel()
        self._stats_data = None       # ← КЭШ
        self._column_progress = {}    # ← КЭШ
        self._column_time = []        # ← КЭШ

        self.vm.statsLoaded.connect(self._on_stats)
        self.vm.columnProgressLoaded.connect(self._on_column_progress)
        self.vm.columnTimeLoaded.connect(self._on_column_time)
        self.vm.noData.connect(self._on_no_data)

        self._build_ui()
        self._load_all()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        panel = QGroupBox("Вид статистики")
        panel_layout = QVBoxLayout(panel)
        self.stat_group = QButtonGroup(self)

        self.rb_sections = QRadioButton("Распределение времени по разделам")
        self.rb_columns = QRadioButton("Прогресс по колонкам")
        self.rb_columns_time = QRadioButton("Время по колонкам")
        self.rb_sections.setChecked(True)

        self.stat_group.addButton(self.rb_sections, 0)
        self.stat_group.addButton(self.rb_columns, 1)
        self.stat_group.addButton(self.rb_columns_time, 2)
        # ВАЖНО: signal → только _render, БЕЗ load_stats
        self.stat_group.buttonClicked.connect(self._render)

        panel_layout.addWidget(self.rb_sections)
        panel_layout.addWidget(self.rb_columns)
        panel_layout.addWidget(self.rb_columns_time)

        options = QHBoxLayout()
        options.addWidget(QLabel("Период:"))
        self.period = QComboBox()
        self.period.addItem("Всё время", "all")
        self.period.addItem("День", "day")
        self.period.addItem("Неделя", "week")
        self.period.addItem("Месяц", "month")
        # Период меняет данные → перезагрузка
        self.period.currentIndexChanged.connect(self._reload)
        options.addWidget(self.period)

        options.addWidget(QLabel("Тип:"))
        self.chart_group = QButtonGroup(self)
        self.rb_pie = QRadioButton("Круговая")
        self.rb_bar = QRadioButton("Столбчатая")
        self.rb_line = QRadioButton("Линейная")
        self.rb_bar.setChecked(True)
        for i, rb in enumerate([self.rb_pie, self.rb_bar, self.rb_line]):
            self.chart_group.addButton(rb, i)
            # Тип графика → только перерисовка, БЕЗ БД
            rb.toggled.connect(self._render)
            options.addWidget(rb)
        options.addStretch()
        panel_layout.addLayout(options)
        layout.addWidget(panel)

        self.figure = Figure(figsize=(9, 5))
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

        self.info = QLabel("")
        layout.addWidget(self.info)

    def _load_all(self):
        """Загружает все данные один раз."""
        self.vm.load_stats(self.period.currentData())
        self.vm.load_column_progress()
        self.vm.load_column_time()

    def _reload(self):
        """Перезагрузка при смене периода."""
        self.vm.load_stats(self.period.currentData())
        self.vm.load_column_progress()
        self.vm.load_column_time()
        # После загрузки — отрисовать
        self._render()

    # ---------- Слоты от ViewModel ----------

    def _on_stats(self, data):
        self._stats_data = data
        self.info.setText(
            f"Всего задач: {data['total']} | Выполнено: {data['done']} | "
            f"В работе: {data['active']} | За период: {data['done_period']}"
        )
        # НЕ вызываем _render здесь — он вызывается отдельно

    def _on_column_progress(self, data):
        self._column_progress = data

    def _on_column_time(self, data):
        self._column_time = data

    def _on_no_data(self):
        self._stats_data = None
        self.info.setText("Нет данных за выбранный период.")

    # ---------- Отрисовка ----------

    def _render(self):
        if self.rb_sections.isChecked():
            self._render_sections()
        elif self.rb_columns.isChecked():
            self._render_columns()
        else:
            self._render_columns_time()

    def _render_sections(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not self._stats_data:
            ax.text(0.5, 0.5, "Нет данных", ha="center", va="center")
            self.canvas.draw()
            return

        sections = [s["name"] for s in self._stats_data["by_section"]]
        totals = [s["total"] / 3600 for s in self._stats_data["by_section"]]

        if not any(totals):
            ax.text(0.5, 0.5, "Нет данных", ha="center", va="center")
            self.canvas.draw()
            return

        if self.rb_pie.isChecked():
            ax.pie(totals, labels=sections, autopct="%1.0f%%")
        elif self.rb_bar.isChecked():
            ax.bar(sections, totals, color="#4a90e2")
            ax.set_ylabel("Часы")
        else:
            ax.plot(sections, totals, marker="o", color="#4a90e2")
            ax.set_ylabel("Часы")
        ax.set_title("Распределение времени по разделам")
        self.canvas.draw()

    def _render_columns(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not self._column_progress:
            ax.text(0.5, 0.5, "Нет колонок", ha="center", va="center")
            self.canvas.draw()
            return

        names = list(self._column_progress.keys())
        counts = [self._column_progress[n]["count"] for n in names]
        colors = [self._column_progress[n]["color"] for n in names]

        bars = ax.bar(names, counts, color=colors)
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.1, str(count),
                    ha="center", fontsize=11, fontweight="bold")
        ax.set_ylabel("Количество задач")
        ax.set_title("Прогресс по колонкам")
        ax.tick_params(axis="x", rotation=15)
        self.canvas.draw()

    def _render_columns_time(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not self._column_time:
            ax.text(0.5, 0.5, "Нет данных", ha="center", va="center")
            self.canvas.draw()
            return

        names = [d["column_name"] for d in self._column_time]
        hours = [d["total_sec"] / 3600 for d in self._column_time]
        colors = [d["color"] for d in self._column_time]

        bars = ax.bar(names, hours, color=colors)
        for bar, h in zip(bars, hours):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05, f"{h:.1f} ч",
                    ha="center", fontsize=10)
        ax.set_ylabel("Часы")
        ax.set_title("Время по колонкам")
        ax.tick_params(axis="x", rotation=15)
        self.canvas.draw()