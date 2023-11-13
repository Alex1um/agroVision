import openpyxl
import numpy as np
import csv
from openpyxl.utils.exceptions import InvalidFileException
from datetime import datetime
import logging
from Date import Date
from NpAnnotBase import NpAnnotBase

class Data(NpAnnotBase):
    name: str
    lat: float
    long: float
    date: Date
    Tmax: float
    Tmin: float
    daily_precipitation_amount: float
    rel_humidity: float
    avg_wind_speed: float

    @classmethod
    def from_file(self, file_path: str):
        # Assuming file is xl
        xl = True
        self = self()
        try:
            xl = openpyxl.open(file_path)
            page = xl.active
            # iterate over annotations and readed from xl cols. NOTE: Assuming annotations and columns are in the same order
            for (k, tpe), readed in zip(self.__annotations__.items(), page.iter_cols(0,len(self.__annotations__), values_only=True)):
                # vectorize type for faster type conversions
                np_func = np.vectorize(tpe)
                # set attribute to readed array, converted to annotation type
                self.__setattr__(k, np_func(np.array(readed)))
        except InvalidFileException as ie:
            logging.info(f"file {file_path} is not a xl file(exception: {ie}). Trying to parse as csv...")
            xl = False
        except Exception as e:
            logging.error(f"Exception {e} occuped while parsing xl file {file_path}")
        if not xl:
            with open(file_path, "r") as f:
                readed = csv.reader(f)
                parsed = list()
                param_count = len(self.__annotations__)
                # iterate over rows
                for row_i, row in enumerate(readed):
                    # check if not empty
                    if row:
                        # prealloc list
                        parsed_row = list()
                        # iterate over values in row
                        for val, (name, type) in zip(row, self.__annotations__.items()):
                            # check tabs and strip
                            if "\t"*5 in val:
                                dbg = val[:val.find("\t")]
                                logging.warning(f"found tabs in '{row}' at '{val}'. truncated to {dbg}")
                                val = dbg
                            try:
                                # convert readed value and add to current (col_name) attribute list
                                parsed_row.append(type(val))
                            except Exception as e:
                                # NOTE: Skipping non-convertible lines
                                logging.warning(f"Exception {e} occuped while parsing {val} to {name} at {row_i} row. Skipping row...")
                                break
                        else:
                            parsed_count = len(parsed_row)
                            if parsed_count == param_count:
                                parsed.append(parsed_row)
                            else:
                                logging.warning(f"parsed not enough params: {parsed_count} != {param_count} at row {row_i}")
                parsed = np.transpose(np.array(parsed))
                # convert attribute lists to np.array
                for k, v in zip(self.__annotations__.keys(), parsed):
                    self.__setattr__(k, v)
        return self


if __name__ == "__main__":
    # print(Data("./meteo_data/BAGAN.csv"))
    # print(Data("./1_первая часть сезона/метео/BAGAN"))
    # print(Data("./combined/BAGAN.csv").__dict__)
    d = Data.from_file("1_первая часть сезона/метео/BAGAN")
    d1 = Data.from_file("1_первая часть сезона/метео/BAGAN")
    d2 = Data.from_file("2_вторая часть сезона/метео/BAGAN.xlsx")
    print(d[1].date)
    print(d["2022/05/05":"2022/05/17"].date)
    print(d["2022/05/25":].date)
    print(len(d1))
    print(len(d2))
    print(len(d1 + d2))
    # import glob
    # for f1, f2 in zip(
    #     sorted(glob.glob("1_первая часть сезона/метео/*"), key=lambda x: x.split("/")[-1]), 
    #     sorted(glob.glob("2_вторая часть сезона/метео/*"), key=lambda x: x.split("/")[-1])
    #     ):
    #     name = f1.split("/")[-1]
    #     print(f1, f2)
    #     d1 = Data(f1)
    #     d2 = Data(f2)
    #     # print(d2)
    #     d1.append(d2)
    #     d1.to_csv(f"combined/{name}.csv")
