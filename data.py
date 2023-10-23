import openpyxl
import numpy as np
import csv
from openpyxl.utils.exceptions import InvalidFileException
from datetime import datetime
import logging


class Date:

    def __init__(self, date: str) -> None:
        if isinstance(date, datetime):
            self.date = date
        elif isinstance(date, str):
            self.date = datetime.strptime(date, "%Y/%m/%d")
        else:
            raise Exception("Cannot parse date")

    def __repr__(self) -> str:
        return datetime.strftime(self.date, "%Y/%m/%d")


class Data:
    name: str
    lat: float
    long: float
    date: Date
    Tmax: float
    Tmin: float
    daily_precipitation_amount: float
    rel_humidity: float
    avg_wind_speed: float

    def __init__(self, file_path: str):
        try:
            xl = openpyxl.open(file_path)
            page = xl.active
            # iterate over annotations and readed from xl cols. NOTE: Assuming annotations and columns are in the same order
            for (k, tpe), readed in zip(self.__annotations__.items(), page.iter_cols(0,len(self.__annotations__), values_only=True)):
                # vectorize type for faster type conversions
                np_func = np.vectorize(tpe)
                # set attribute to readed array, converted to annotation type
                self.__setattr__(k, np_func(np.array(readed)))
        except InvalidFileException:
            with open(file_path, "r") as f:
                readed = csv.reader(f)
                # setup empty lists to read into them for each attribute
                for k in self.__annotations__.keys():
                    self.__setattr__(k, list())
                # iterate over rows
                for row in readed:
                    # iterate over columns
                    for (col_name, col_data), v in zip(self.__dict__.items(), row):
                        # check tabs and strip
                        if "\t"*5 in v:
                            dbg = v[:v.find("\t")]
                            logging.warning(f"found tabs in '{row}' at '{v}'. truncated to {dbg}")
                            v = dbg
                        try:
                            # convert readed value and add to current (col_name) attribute list
                            col_data.append(self.__annotations__[col_name](v))
                        except Exception as e:
                            # NOTE: Skipping non-convertible lines
                            logging.warning(f"Exception {e} occuped while parsing {v} to {self.__annotations__[col_name]}.skipping row...")
                # convert attribute lists to np.array
                for k, v in self.__dict__.items():
                    self.__setattr__(k, np.array(v))

    def append(self, data):
        for sk, sv in self.__dict__.items():
            self.__setattr__(sk, np.append(sv, data.__getattribute__(sk)))

    def to_csv(self, file: str):
        with open(file, "w") as f:
            wr = csv.writer(f)
            wr.writerows(zip(*self.__dict__.values()))

    def __repr__(self) -> str:
        return repr(np.array(self.__dict__.values()))

if __name__ == "__main__":
    # print(Data("./meteo_data/BAGAN.csv"))
    # print(Data("./1_первая часть сезона/метео/BAGAN"))
    # print(Data("./combined/BAGAN.csv").__dict__)
    import glob
    for f1, f2 in zip(
        sorted(glob.glob("1_первая часть сезона/метео/*"), key=lambda x: x.split("/")[-1]), 
        sorted(glob.glob("2_вторая часть сезона/метео/*"), key=lambda x: x.split("/")[-1])
        ):
        name = f1.split("/")[-1]
        print(f1, f2)
        d1 = Data(f1)
        d2 = Data(f2)
        d1.append(d2)
        d1.to_csv(f"combined/{name}.csv")
