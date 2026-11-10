from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QFrame, QListWidget, QListWidgetItem, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from app.viewmodels.stats_vm import StatsViewModel

class StatsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = StatsViewModel()
        self.data = {}
        
        layout = QVBoxLayout(self)
        
        top_layout = QHBoxLayout()
        
        self.combo_metric = QComboBox()
        self.combo_metric.addItems(["Задачи по колонкам", "Выполнено за период", "Затраченное время"])
        self.combo_metric.currentIndexChanged.connect(self.on_metric_changed)
        
        self.combo_chart = QComboBox()
        self.combo_chart.currentIndexChanged.connect(self.build_chart)
        
        self.combo_time_target = QComboBox()
        self.combo_time_target.addItems(["Задача", "Раздел задач", "Задачи для сравнения", "Разделы для сравнения"])
        self.combo_time_target.setVisible(False)
        self.combo_time_target.currentIndexChanged.connect(self.on_time_target_changed)
        
        self.combo_single_select = QComboBox()
        self.combo_single_select.setVisible(False)
        self.combo_single_select.currentIndexChanged.connect(self.build_chart)
        
        self.combo_period = QComboBox()
        self.combo_period.addItems(["За день", "За неделю", "За месяц"])
        self.combo_period.setVisible(False)
        self.combo_period.currentIndexChanged.connect(self.load_data)
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.clicked.connect(self.load_data)
        
        top_layout.addWidget(QLabel("<b>Показатель:</b>"))
        top_layout.addWidget(self.combo_metric)
        top_layout.addWidget(QLabel("<b>Тип:</b>"))
        top_layout.addWidget(self.combo_chart)
        top_layout.addWidget(self.combo_time_target)
        top_layout.addWidget(self.combo_single_select)
        top_layout.addWidget(self.combo_period)
        top_layout.addWidget(self.btn_refresh)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        self.compare_list = QListWidget()
        self.compare_list.setMaximumHeight(80)
        self.compare_list.setVisible(False)
        self.compare_list.itemChanged.connect(self.build_chart)
        layout.addWidget(self.compare_list)
        
        # --- ГРАФИК ---
        self.chart_frame = QFrame()
        self.chart_frame.setObjectName("chart_frame")
        chart_layout = QHBoxLayout(self.chart_frame)
        
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedSize(500, 300)
        chart_layout.addWidget(self.canvas)
        
        self.compare_text = QTextEdit()
        self.compare_text.setReadOnly(True)
        self.compare_text.setVisible(False)
        self.compare_text.setObjectName("compare_text")
        chart_layout.addWidget(self.compare_text)
        
        layout.addWidget(self.chart_frame)
        
        # --- СВОДКА ---
        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("summary_frame")
        summary_layout = QHBoxLayout(self.summary_frame)
        
        self.lbl_total = QLabel("Всего задач: 0")
        self.lbl_in_progress = QLabel("В работе: 0")
        self.lbl_done = QLabel("Выполнено: 0")
        self.lbl_time = QLabel("Затраченное время: -")
        
        for lbl in [self.lbl_total, self.lbl_in_progress, self.lbl_done, self.lbl_time]:
            lbl.setProperty("class", "summary_label")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(lbl)
        layout.addWidget(self.summary_frame)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()

    def format_time_str(self, sec):
        if sec == 0: return "-"
        d = sec // 86400
        h = (sec % 86400) // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        
        parts = []
        if d > 0: parts.append(f"{d} дн")
        if h > 0: parts.append(f"{h} ч")
        
        if m > 0 or (d == 0 and h == 0):
            if s > 0 and m < 5: 
                parts.append(f"{m} мин {s} сек")
            else:
                parts.append(f"{m} мин")
                
        return " ".join(parts) if parts else "< 1 сек"

    def load_data(self):
        period_idx = self.combo_period.currentIndex()
        days = 1 if period_idx == 0 else (7 if period_idx == 1 else 30)
        
        self.data = self.vm.get_stats_data(days=days)
        if not self.data:
            return
            
        self.update_summary()
        self.on_metric_changed()

    def on_metric_changed(self):
        metric = self.combo_metric.currentText()
        
        self.combo_chart.clear()
        self.combo_time_target.setVisible(False)
        self.combo_period.setVisible(False)
        self.combo_single_select.setVisible(False)
        self.compare_list.setVisible(False)
        self.compare_text.setVisible(False)
        
        if metric == "Задачи по колонкам":
            self.combo_chart.addItems(["Столбчатая", "Круговая"])
            self.combo_chart.setVisible(True)
            self.build_chart()
            
        elif metric == "Выполнено за период":
            self.combo_period.setVisible(True)
            self.combo_time_target.setVisible(True)
            self.combo_time_target.clear()
            self.combo_time_target.addItems(["Задачи", "Разделы"])
            try:
                self.combo_time_target.currentIndexChanged.disconnect()
            except:
                pass
            self.combo_time_target.currentIndexChanged.connect(self.on_period_target_changed)
            self.on_period_target_changed()
            
        elif metric == "Затраченное время":
            self.combo_time_target.setVisible(True)
            self.combo_time_target.clear()
            self.combo_time_target.addItems(["Задача", "Раздел задач", "Задачи для сравнения", "Разделы для сравнения"])
            try:
                self.combo_time_target.currentIndexChanged.disconnect()
            except:
                pass
            self.combo_time_target.currentIndexChanged.connect(self.on_time_target_changed)
            self.on_time_target_changed()

    def on_period_target_changed(self):
        target = self.combo_time_target.currentText()
        self.combo_chart.clear()
        
        if target == "Задачи":
            self.combo_chart.addItems(["Столбчатая"]) 
            self.combo_chart.setVisible(True)
            self.combo_single_select.setVisible(False)
        else:
            self.combo_chart.addItems(["Столбчатая"])
            self.combo_chart.setVisible(True)
            self.combo_single_select.setVisible(True)
            self.combo_single_select.clear()
            for s in self.data.get("sections_list", []):
                self.combo_single_select.addItem(s["name"], s["id"])
                
        self.build_chart()

    def on_time_target_changed(self):
        target = self.combo_time_target.currentText()
        self.combo_chart.clear()
        self.combo_chart.addItems(["Столбчатая"])
        self.combo_chart.setVisible(True)
        
        self.combo_single_select.clear()
        self.compare_list.clear()
        
        if target in ["Задача", "Раздел задач"]:
            self.combo_single_select.setVisible(True)
            self.compare_list.setVisible(False)
            self.compare_text.setVisible(False)
            if target == "Задача":
                self.combo_single_select.addItems(self.data.get("tasks_time", {}).keys())
            else:
                self.combo_single_select.addItems(self.data.get("sections_time", {}).keys())
        elif "сравнения" in target:
            self.combo_single_select.setVisible(False)
            self.compare_list.setVisible(True)
            self.compare_text.setVisible(True)
            
            items = self.data.get("tasks_time", {}).keys() if "Задачи" in target else self.data.get("sections_time", {}).keys()
            for item_name in items:
                item = QListWidgetItem(item_name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.compare_list.addItem(item)
        
        self.build_chart()

    def update_summary(self):
        summary = self.data.get("summary", {})
        self.lbl_total.setText(f"Всего задач: {summary.get('total', 0)}")
        self.lbl_in_progress.setText(f"В работе: {summary.get('in_progress', 0)}")
        self.lbl_done.setText(f"Выполнено: {summary.get('done', 0)}")

    def build_chart(self):
        if not self.data: return
        self.figure.clear()
        
        # --- ОПРЕДЕЛЕНИЕ ТЕМЫ ---
        window = self.window()
        is_dark = False
        if window:
            bg_color = window.palette().color(QPalette.ColorRole.Window)
            is_dark = bg_color.lightness() < 128
            
        bg_color = '#1E1E1E' if is_dark else '#FFFFFF'
        text_color = '#E0E0E0' if is_dark else '#212529'
        
        self.figure.patch.set_facecolor(bg_color)
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        ax.title.set_color(text_color)
        for spine in ax.spines.values():
            spine.set_color(text_color)
        # -------------------------
            
        metric = self.combo_metric.currentText()
        
        self.lbl_time.setText("Затраченное время: -")

        if metric == "Задачи по колонкам":
            d = self.data.get("tasks_by_column", {})
            d_filtered = {k: v for k, v in d.items() if v > 0}
            
            if not d_filtered:
                ax.text(0.5, 0.5, "Нет данных о задачах", ha='center', va='center', color='red', fontsize=14)
            else:
                chart_type = self.combo_chart.currentText()
                if chart_type == "Круговая":
                    ax.pie(d_filtered.values(), labels=d_filtered.keys(), autopct='%1.0f%%')
                else:
                    ax.bar(d_filtered.keys(), d_filtered.values(), color='#F97316')
                    ax.set_ylabel("Количество задач") 
                
        elif metric == "Выполнено за период":
            target = self.combo_time_target.currentText()
            if target == "Задачи":
                d = self.data.get("completed_by_days", {})
                if sum(d.values()) == 0:
                    ax.text(0.5, 0.5, "Нет выполненных задач за период", ha='center', va='center', color='red', fontsize=14)
                else:
                    keys = list(d.keys())
                    vals = list(d.values())
                    ax.bar(range(len(keys)), vals, color='#F97316')
                    ax.set_xticks(range(len(keys)))
                    ax.set_xticklabels(keys, rotation=45, ha="right")
                    ax.set_title("Выполнено задач по дням")
                    ax.set_ylabel("Количество задач") 
            else:
                d = self.data.get("completed_by_sections", {})
                sel = self.combo_single_select.currentText()
                if sel and sel != "Все разделы":
                    d = {sel: d.get(sel, 0)}
                
                if not d or sum(d.values()) == 0:
                    ax.text(0.5, 0.5, "Нет выполненных задач за период", ha='center', va='center', color='red', fontsize=14)
                else:
                    ax.bar(d.keys(), d.values(), color='#F97316')
                    ax.set_ylabel("Количество задач") 
                    
        elif metric == "Затраченное время":
            target = self.combo_time_target.currentText()
            
            if "сравнения" in target:
                selected_items = [self.compare_list.item(i).text() for i in range(self.compare_list.count()) 
                                  if self.compare_list.item(i).checkState() == Qt.CheckState.Checked]
                if len(selected_items) < 2:
                    ax.text(0.5, 0.5, "Выберите 2+ элемента", ha='center', va='center', color='red', fontsize=14)
                    self.compare_text.clear()
                    self.canvas.draw()
                    return
                
                raw_data = self.data.get("tasks_time", {}) if "Задачи" in target else self.data.get("sections_time", {})
                filtered_data = {k: raw_data.get(k, 0) for k in selected_items}
                
                if sum(filtered_data.values()) == 0:
                    ax.text(0.5, 0.5, "Нет данных о времени", ha='center', va='center', color='red', fontsize=14)
                else:
                    plot_data = {k: round(v / 60, 1) for k, v in filtered_data.items()}
                    ax.bar(plot_data.keys(), plot_data.values(), color='#F97316')
                    ax.set_ylabel("Время (в минутах)") 
                    
                    total_sec = sum(filtered_data.values())
                    self.lbl_time.setText(f"Общее время: {self.format_time_str(total_sec)}")
                    
                    text_lines = ["<b>Сравнение:</b><br>"]
                    for k, v in filtered_data.items():
                        text_lines.append(f"{k}: {self.format_time_str(v)}")
                    self.compare_text.setHtml("<br>".join(text_lines))
                
            else:
                sel = self.combo_single_select.currentText()
                raw_data = self.data.get("tasks_time", {}) if target == "Задача" else self.data.get("sections_time", {})
                sec = raw_data.get(sel, 0)
                
                if sec == 0:
                    ax.text(0.5, 0.5, "Нет данных о времени", ha='center', va='center', color='red', fontsize=14)
                else:
                    self.lbl_time.setText(f"Время ({sel}): {self.format_time_str(sec)}")
                    mins = round(sec / 60, 1)
                    ax.bar([sel], [mins], color='#F97316')
                    ax.set_ylabel("Время (в минутах)") 
                    
                self.compare_text.setVisible(False)

        self.figure.tight_layout()
        self.canvas.draw()