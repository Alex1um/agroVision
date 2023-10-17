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


    def __init__(self) -> None:
        self.name = np.array([])
        self.lat = np.array([])
        self.long = np.array([])
        self.date = np.array([])
        self.Tmax = np.array([])  
        self.Tmin = np.array([])
        self.daily_precipitation_amount = np.array([])
        self.rel_humidity = np.array([])
        self.avg_wind_speed = np.array([])

    @classmethod
    def from_file(cls, file_path: str):
        cls = cls()
        try:
            xl = openpyxl.open(file_path)
            page = xl.active
            for k, readed in zip(vars(cls).keys(), page.iter_cols(0,len(vars(cls)), values_only=True)):
                cls.__setattr__(k, np.array(readed))
        except InvalidFileException:
            with open(file_path, "r") as f:
                readed = csv.reader(f)
                for k in vars(cls).keys():
                    cls.__setattr__(k, list())
                for row in readed:
                    for (col_name, col_data), v in zip(vars(cls).items(), row):
                        col_data.append(cls.__annotations__[col_name](v))
                for k, v in vars(cls).items():
                    cls.__setattr__(k, np.array(v))
        return cls

    def __repr__(self) -> str:
        return repr(np.array(vars(self).values()))

if __name__ == "__main__":
    print(Data.from_file("./meteo_data/BAGAN"))