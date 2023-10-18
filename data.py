import openpyxl
import numpy as np
import csv
from openpyxl.utils.exceptions import InvalidFileException

class Data:
    name: str
    lat: float
    long: float
    date: str
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
                self.__setattr__(k, np.array(readed))
        except InvalidFileException:
            with open(file_path, "r") as f:
                readed = csv.reader(f)
                for k in self.__annotations__.keys():
                    self.__setattr__(k, list())
                for row in readed:
                    for (col_name, col_data), v in zip(vars(self).items(), row):
                        col_data.append(self.__annotations__[col_name](v))
                for k, v in vars(self).items():
                    self.__setattr__(k, np.array(v))

    def __repr__(self) -> str:
        return repr(np.array(vars(self).values()))

if __name__ == "__main__":
    print(Data.from_file("./meteo_data/BAGAN"))