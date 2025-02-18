import pandas as pd

class DataHandler:
    def __init__(self):
        self.data = None

    def load_data(self, file_path):
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xlsm'):
                self.data = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            else:
                raise ValueError("Неподдерживаемый формат файла")
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def sort_data(self, column, ascending=True):
        try:
            self.data.sort_values(by=column, ascending=ascending, inplace=True)
            print(f"Сортировка выполнена по столбцу '{column}' (ascending={ascending})")
        except Exception as e:
            print(f"Ошибка сортировки данных: {e}")

    def sort_by_row(self, row_index, ascending=True):
        if True:
            row_values = self.data.iloc[row_index]
            print(row_values)
            sorted_columns = row_values.sort_values(ascending=ascending).index
            print(sorted_columns)
            self.data = self.data.loc[:, sorted_columns]
            print(f"Сортировка выполнена по строке {row_index} (ascending={ascending})")
        # except Exception as e:
        #     print(f"Ошибка сортировки строк: {e}")
