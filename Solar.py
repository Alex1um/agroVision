import openpyxl
import numpy as np
import csv
from openpyxl.utils.exceptions import InvalidFileException
from datetime import datetime
import logging
from openpyxl.worksheet.worksheet import Worksheet
from Date import Date
from NpAnnotBase import NpAnnotBase


class Solar(NpAnnotBase):
    date: Date
    radiation: float

    @classmethod
    def from_file(self, file_path: str, year: int = 2022) -> None:
        # for parsing 
        Date.CURRENT_YEAR = year
        self = self()
        is_xl = True
        param_count = len(self.__annotations__)
        # xl same as in data
        try:
            xl = openpyxl.open(file_path, read_only=True, data_only=True)
            sheet: Worksheet = xl.active
            parsed = list()
            # row_i for logging errors
            for row_i, row in enumerate(sheet.iter_rows(values_only=True)):
                parsed_row = list()
                for (name, type), val in zip(self.__annotations__.items(), row):
                    if val:
                        # try parse readed value to annotation type
                        try:
                            parsed_row.append(type(val))
                        except Exception as e:
                            logging.warning(
                                f"Exception {e} occuped while parsing {val} to {name} at {row_i} row. Skipping row...")
                            break
                else:
                    # check parsed count
                    parsed_count = len(parsed_row)
                    if param_count == param_count:
                        parsed.append(parsed_row)
                    else:
                        logging.warning(f"parsed not enough params: {parsed_count} != {param_count} at row {row_i}")
            # to np array
            parsed = np.transpose(np.array(parsed))
            for k, v in zip(self.__annotations__.keys(), parsed):
                self.__setattr__(k, v)
        except InvalidFileException as ie:
            logging.info(f"Cannot open file {file_path} as xl: {ie}. Trying parse as plain text")
            is_xl = False
        except Exception as e:
            logging.error(f"Cnnot parse file {file_path}: {e}")
        # plain text
        if not is_xl:
            with open(file_path, "r") as f:
                # first line = name
                name = f.readline().strip()
                # second = mnth/year
                months = f.readline().strip().split(" " * 4)
                months_count = len(months)
                values = [0] * months_count
                for i in range(months_count):
                    values[i] = list()

                # read while empty line
                rl = f.readline().strip()
                while rl:
                    parsed_values = map(float, rl.split(" " * 4))
                    for lst, val in zip(values, parsed_values):
                        lst.append(val)
                    rl = f.readline().strip()
                self.date = list()
                self.radiation = list()
                # convert to arrays
                for month, values in zip(months, values):
                    for i, val in enumerate(values):
                        self.date.append(Date(datetime.strptime(f"{i + 1}/{month}", "%d/%m/%y")))
                        self.radiation.append(val)
                self.date = np.array(self.date)
                self.radiation = np.array(self.radiation)
        return self


if __name__ == "__main__":
    # print(Solar("2_вторая часть сезона/солнечная радиация/sun_bagan.xlsx"))
    print(Solar.from_file("1_первая часть сезона/солнечная радиация/sun_bagan"))
