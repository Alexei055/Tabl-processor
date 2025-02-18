import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QWidget, QLabel, QTableWidget, QTableWidgetItem, QComboBox, QProgressDialog, QLineEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
from data_handler import DataHandler

class WorkerThread(QThread):
    task_done = pyqtSignal()
    chart_ready = pyqtSignal(object, object)  # Сигнал для передачи данных графика

    def __init__(self, task_function):
        super().__init__()
        self.task_function = task_function

    def run(self):
        self.task_function()
        self.task_done.emit()

class TabularApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Табличный процессор")
        self.setGeometry(100, 100, 800, 600)

        self.handler = DataHandler()
        self.sort_ascending = True
        self.progress_dialog = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Импортируйте таблицу")
        layout.addWidget(self.label)

        self.table = QTableWidget()
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by_column)
        self.table.verticalHeader().sectionClicked.connect(self.sort_by_row)
        layout.addWidget(self.table)

        self.load_button = QPushButton("Загрузить файл")
        self.load_button.clicked.connect(self.load_file)
        layout.addWidget(self.load_button)

        # Выпадающие списки для выбора столбцов
        self.x_axis_combo = QComboBox()
        self.y_axis_combo = QComboBox()
        layout.addWidget(QLabel("Выберите X-ось:"))
        layout.addWidget(self.x_axis_combo)
        layout.addWidget(QLabel("Выберите Y-ось:"))
        layout.addWidget(self.y_axis_combo)

        self.chart_button = QPushButton("Построить диаграмму")
        self.chart_button.clicked.connect(self.plot_chart)
        layout.addWidget(self.chart_button)

        # Поля для поиска и замены (по нажатию на кнопку)
        self.search_replace_button = QPushButton("Поиск и замена данных")
        self.search_replace_button.clicked.connect(self.show_search_replace_window)
        layout.addWidget(self.search_replace_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_search_replace_window(self):
        self.search_replace_widget = QWidget()
        self.search_replace_widget.setWindowTitle("Поиск и замена данных")
        self.search_replace_widget.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска")
        layout.addWidget(self.search_input)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Введите текст для замены")
        layout.addWidget(self.replace_input)

        self.replace_button = QPushButton("Заменить")
        self.replace_button.clicked.connect(self.search_and_replace)
        layout.addWidget(self.replace_button)

        self.search_replace_widget.setLayout(layout)
        self.search_replace_widget.show()

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Excel Files (*.xlsx *.xlsm);;CSV Files (*.csv)")

        if file_path:
            self.show_progress("Загрузка файла...")
            self.worker = WorkerThread(lambda: self.handler.load_data(file_path))
            self.worker.task_done.connect(self.on_file_loaded)
            self.worker.start()

    def on_file_loaded(self):
        self.hide_progress()
        print(f"Данные загружены: {self.handler.data.head()}")  # Отладочный вывод
        self.display_data()
        self.populate_column_selectors()

    def populate_column_selectors(self):
        if self.handler.data is not None:
            columns = self.handler.data.columns
            self.x_axis_combo.clear()
            self.y_axis_combo.clear()
            self.x_axis_combo.addItems(columns)
            self.y_axis_combo.addItems(columns)

    def display_data(self):
        if isinstance(self.handler.data, pd.DataFrame):
            self.label.setText("Данные загружены")

            # Очистка таблицы
            self.table.clear()
            self.table.setRowCount(0)

            # Настройка таблицы
            self.table.setRowCount(len(self.handler.data))
            self.table.setColumnCount(len(self.handler.data.columns))
            self.table.setHorizontalHeaderLabels(self.handler.data.columns)

            # Заполнение таблицы
            for i, row in enumerate(self.handler.data.itertuples(index=False)):
                for j, value in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))

            # Принудительное обновление интерфейса
            self.table.viewport().update()
        else:
            self.label.setText("Ошибка загрузки данных")

    def sort_by_column(self, column_index):
        if self.handler.data is None:
            self.label.setText("Ошибка: данные не загружены")
            return

        column_name = self.table.horizontalHeaderItem(column_index).text()
        print(f"Сортировка по столбцу: {column_name}")  # Отладочный вывод

        self.show_progress("Сортировка столбцов...")
        self.worker = WorkerThread(lambda: self.handler.sort_data(column_name, ascending=self.sort_ascending))
        self.worker.task_done.connect(lambda: self.on_sort_done(column_index))
        self.worker.start()

    def on_sort_done(self, column_index):
        self.sort_ascending = not self.sort_ascending
        self.hide_progress()
        self.display_data()

    def sort_by_row(self, row_index):
        if self.handler.data is None:
            self.label.setText("Ошибка: данные не загружены")
            return

        print(f"Сортировка по строке: {row_index}")  # Отладочный вывод

        self.show_progress("Сортировка строк...")
        self.worker = WorkerThread(lambda: self.handler.sort_by_row(row_index, ascending=self.sort_ascending))
        self.worker.task_done.connect(self.on_sort_done)
        self.worker.start()

    def plot_chart(self):
        if self.handler.data is None:
            self.label.setText("Ошибка: данные не загружены")
            return

        x_column = self.x_axis_combo.currentText()
        y_column = self.y_axis_combo.currentText()

        if not x_column or not y_column:
            self.label.setText("Выберите столбцы для построения диаграммы")
            return

        self.show_progress("Построение диаграммы...")
        self.worker = WorkerThread(lambda: self.prepare_chart_data(x_column, y_column))
        self.worker.chart_ready.connect(self.render_chart)  # Подключение сигнала для построения графика
        self.worker.task_done.connect(self.hide_progress)
        self.worker.start()

    def prepare_chart_data(self, x_column, y_column):
        try:
            x = self.handler.data[x_column]
            y = self.handler.data[y_column]
            self.worker.chart_ready.emit(x, y)  # Отправка данных для построения графика
        except Exception as e:
            print(f"Ошибка при подготовке данных диаграммы: {e}")
            self.label.setText("Ошибка при подготовке данных диаграммы")

    def render_chart(self, x, y):
        try:
            plt.figure(figsize=(8, 6))
            plt.bar(x, y, color='skyblue')
            plt.title("Диаграмма", fontsize=14)
            plt.xlabel(x.name, fontsize=12)
            plt.ylabel(y.name, fontsize=12)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Ошибка при построении диаграммы: {e}")
            self.label.setText("Ошибка при построении диаграммы")

    def show_progress(self, message):
        self.progress_dialog = QProgressDialog(message, None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Пожалуйста, подождите")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

    def hide_progress(self):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    def search_and_replace(self):
        if self.handler.data is None:
            self.label.setText("Ошибка: данные не загружены")
            return

        search_term = self.search_input.text().strip()
        replace_term = self.replace_input.text().strip()

        if not search_term:
            self.label.setText("Заполните поле поиска")
            return

        if not replace_term:
            self.label.setText("Заполните поле замены")
            return

        self.show_progress("Поиск и замена данных...")

        def task():
            try:
                print(f"Замена '{search_term}' на '{replace_term}'")  # Отладка
                print("Данные до замены:\n", self.handler.data.head())  # Отладка
                # Преобразуем данные к строковому типу перед заменой
                self.handler.data = self.handler.data.astype(str).replace(search_term, replace_term, regex=True)
                print("Данные после замены:\n", self.handler.data.head())  # Отладка
            except Exception as e:
                print(f"Ошибка при замене данных: {e}")

        self.worker = WorkerThread(task)
        self.worker.task_done.connect(self.on_replace_done)
        self.worker.start()

    def on_replace_done(self):
        self.hide_progress()
        self.search_replace_widget.close()  # Закрываем окно поиска и замены
        self.display_data()
        self.label.setText("Замена завершена")
