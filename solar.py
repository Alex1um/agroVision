import openpyxl
import numpy as np
import csv
from openpyxl.utils.exceptions import InvalidFileException
from datetime import datetime
import logging
from openpyxl.worksheet.worksheet import Worksheet

class XlNumDate:

    def __init__(self, raw_date: float) -> None:
        if isinstance(raw_date, datetime):
            self.date = raw_date
        elif isinstance(raw_date, float):
            d, m = divmod(raw_date, 1)
            m = int(round(m, 2) * 100)
            d = int(d)
            self.date = datetime(2023, m, d)
        else:
            raise ValueError(f"Cannot parse date from value {raw_date}")

    def __repr__(self) -> str:
        return datetime.strftime(self.date, "%Y/%m/%d")

class Solar:
    date: XlNumDate
    radiation: float

    def __init__(self, file_path: str) -> None:
        is_xl = True
        param_count = len(self.__annotations__)
        try:
            xl = openpyxl.open(file_path, read_only=True, data_only=True)
            sheet: Worksheet = xl.active
            parsed = list()
            for row_i, row in enumerate(sheet.iter_rows(values_only=True)):
                parsed_row = list()
                for (name, type), val in zip(self.__annotations__.items(), row):
                    if val: 
                        try:
                            parsed_row.append(type(val))
                        except Exception as e:
                            logging.warning(f"Exception {e} occuped while parsing {val} to {name} at {row_i} row. Skipping row...")
                            break
                else:
                    if len(parsed_row) == param_count:
                        parsed.append(parsed_row)
            parsed = np.transpose(np.array(parsed))
            for k, v in zip(self.__annotations__.keys(), parsed):
                self.__setattr__(k, v)
        except InvalidFileException as ie:
            logging.info(f"Cannot open file {file_path} as xl: {ie}. Trying parse as plain text")
            is_xl = False
        except Exception as e:
            logging.error(f"Cnnot parse file {file_path}: {e}")
        # if not is_xl:

    def __repr__(self) -> str:
        return repr(np.array(self.__dict__.values()))

if __name__ == "__main__":
    print(Solar("2_вторая часть сезона/солнечная радиация/sun_bagan.xlsx"))
