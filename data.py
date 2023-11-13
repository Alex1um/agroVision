import openpyxl
import numpy as np
import csv
from openpyxl.utils.exceptions import InvalidFileException
from datetime import datetime
import logging


class Date:

    def __init__(self, date: str | datetime) -> None:
        if isinstance(date, datetime):
            self.date = date
        elif isinstance(date, str):
            self.date = datetime.strptime(date, "%Y/%m/%d")
        elif isinstance(date, Date):
            self.date = date.date
        else:
            raise Exception("Cannot parse date")
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Date):
            return self.date == __value.date
        elif isinstance(__value, datetime):
            return self.date == __value
        else:
            raise ValueError(f"operator '==' of {type(self)} and {type(__value)} is not implemented")
    
    def __gt__(self, __value: object) -> bool:
        if isinstance(__value, Date):
            return self.date > __value.date
        elif isinstance(__value, datetime):
            return self.date > __value
        else:
            raise ValueError(f"operator '>' of {type(self)} and {type(__value)} is not implemented")

    def __lt__(self, __value: object) -> bool:
        return (not self > __value) and self != __value

    def __le__(self, __value: object) -> bool:
        return not self > __value
    
    def __ge__(self, __value: object) -> bool:
        return self > __value or self == __value

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

    def __init__(self) -> None:
        for k, v in self.__annotations__.items():
            self.__setattr__(k, np.array([], dtype=v))

    @classmethod
    def from_file(self, file_path: str):
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
        return self

    def append(self, data):
        for sk, sv in self.__dict__.items():
            self.__setattr__(sk, np.append(sv, data.__getattribute__(sk)))

    def to_csv(self, file: str):
        with open(file, "w") as f:
            wr = csv.writer(f)
            wr.writerows(zip(*self.__dict__.values()))
    
    def __getitem__(self, elem: str | int):
        """
        returns new Data object from original Data slices

        Usage:

        data["2022/05/03":"2022/05/15"] -- slice of str dates only this format can be used

        data[5:10] -- slice of indices

        data["2022/05/03":10] -- combined slice of str date and indexes

        data[datetime(2022, 05, 10)] -- datetime or Date slices also can be used
        
        data["2022/05/15":] -- empty stop slice

        data[::2] -- step slices also can be used
        """
        new = Data()
        if isinstance(elem, slice):
            start = None
            stop = None
            step = None
            if isinstance(elem.start, int):
                start = elem.start
            if isinstance(elem.stop, int):
                stop = elem.stop
            if isinstance(elem.step, int):
                step = elem.step
            islice = slice(start, stop, step)
            date_arr = self.date[islice]
            date_cond = None
            if isinstance(elem.start, (str, datetime)):
                date_cond = date_arr >= Date(elem.start)
            if isinstance(elem.stop, (str, datetime)):
                if date_cond is None:
                    date_cond = date_arr < Date(elem.stop)
                else:
                    date_cond = (date_arr < Date(elem.stop)) & date_cond
            if date_cond is not None:
                idx = np.where(date_cond)
            else:
                idx = islice
            for k, v in  self.__dict__.items():
                new.__setattr__(k, np.array(v[idx]))
        else:
            if isinstance(elem, int):
                index = elem
            elif isinstance(elem, (str, datetime)):
                index = np.where(self.date == Date(elem))
            for k, v in  self.__dict__.items():
                new.__setattr__(k, np.array(v[index]))
        return new
            

    def __repr__(self) -> str:
        return repr(np.array(self.__dict__.values()))

if __name__ == "__main__":
    # print(Data("./meteo_data/BAGAN.csv"))
    # print(Data("./1_первая часть сезона/метео/BAGAN"))
    # print(Data("./combined/BAGAN.csv").__dict__)
    d = Data.from_file("meteo_data/BAGAN.csv")
    # print(d[1])
    # print(d["2022/05/05":"2022/05/17"])
    # print(d["2022/05/25":])
    # import glob
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
