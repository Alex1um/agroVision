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
            for k, readed in zip(self.__annotations__.keys(), page.iter_cols(0,len(vars(self)), values_only=True)):
                tpe = self.__annotations__[k]
                np_func = np.vectorize(tpe)
                self.__setattr__(k, np_func(np.array(readed)))
        except InvalidFileException:
            with open(file_path, "r") as f:
                readed = csv.reader(f)
                for k in self.__annotations__.keys():
                    self.__setattr__(k, list())
                for row in readed:
                    for (col_name, col_data), v in zip(vars(self).items(), row):
                        if "\t"*5 in v:
                            dbg = v[:v.find("\t")]
                            logging.warning(f"found tabs in '{row}' at '{v}'. truncated to {dbg}")
                            v = dbg
                        try:
                            col_data.append(self.__annotations__[col_name](v))
                        except Exception as e:
                            logging.warning(f"Exception {e} occuped while parsing {v} to {self.__annotations__[col_name]}.skipping row...")
                for k, v in vars(self).items():
                    self.__setattr__(k, np.array(v))

    def append(self, data):
        for sk, sv in vars(self).items():
            self.__setattr__(sk, np.append(sv, data.__getattribute__(sk)))
    
    def to_csv(self, file: str):
        with open(file, "w") as f:
            wr = csv.writer(f)
            wr.writerows(zip(*vars(self).values()))


    def __repr__(self) -> str:
        return repr(np.array(vars(self).values()))

if __name__ == "__main__":
    # print(Data("./meteo_data/BAGAN.csv"))
    # print(Data("./1_первая часть сезона/метео/BAGAN"))
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