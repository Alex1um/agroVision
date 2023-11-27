import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
import numpy as np
import os


class ResultTable:

    def __init__(self, xl_path: str, file_names_path: str, out_file: str = None) -> None:
        self.files = self.get_file_names(file_names_path)
        self.xl = openpyxl.open(xl_path)
        self.sheet: Worksheet = self.xl.active
        if out_file is not None:
            self.out = out_file
        else:
            self.out = xl_path

    def iter(self):
        for row in self.sheet.iter_rows(4):
            self.crow = row
            values = [e.value for e in row if e is not None]
            if len(values) >= 14 and all(e is not None for e in values[:6]):
                yield (self.files[values[0]], (values[1], values[2]), np.array(values[3:6]), np.array(values[10:13]))
        self.xl.save(self.out)

    def set_current_row(self, values: tuple[int, int, int]):
        if values:
            for c, v in zip(self.crow[6:9], values):
                c.value = v

    @staticmethod
    def find_path_in_dir(dir: str, file_name: str):
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file.startswith(file_name) and os.path.splitext(file)[0] == file_name:
                    return os.path.join(root, file)
        return None

    @staticmethod
    def get_file_names(xl_table: str) -> dict[str, tuple[str, str]]:
        d = dict()
        xl = openpyxl.open(xl_table, read_only=True)
        sheet: Worksheet = xl.active
        for row in sheet.iter_rows(2, values_only=True):
            if all(row):
                d[row[0]] = (row[1], row[2])
        return d


# if __name__ == "__main__":
#     # print(ResultTable.get_file_names("excels/Перечень_район_метеостанция.xlsx"))
#     table = ResultTable("excels/Таблица вычислений_НСО_районы_2022.xlsx", "excels/Перечень_район_метеостанция.xlsx")
#     for (meteo_file_name, solar_file_name), (date_start, date_end), HI, res_values in table.iter():
#         meteo_file_path = table.find_path_in_dir("1_первая часть сезона", meteo_file_name)
#         solar_file_path = table.find_path_in_dir("1_первая часть сезона", solar_file_name)
#         # meteo = Data(meteo_file_path)
#         # solar = Data(solar_file_path)
#         # ...
#         table.set_current_row((2, 1, 1))
