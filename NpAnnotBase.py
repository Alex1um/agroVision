import numpy as np
import csv
from Date import Date
from datetime import datetime


class NpAnnotBase:

    def __init__(self) -> None:
        for k, v in self.__annotations__.items():
            self.__setattr__(k, np.array([], dtype=v))

    def __iadd__(self, data):
        for sk, sv in self.__dict__.items():
            self.__setattr__(sk, np.append(sv, data.__getattribute__(sk)))
        return self

    def __add__(self, data):
        new = self.__class__()
        for sk, sv in new.__dict__.items():
            new.__setattr__(sk, np.append(sv, self.__getattribute__(sk)))
        for sk, sv in new.__dict__.items():
            new.__setattr__(sk, np.append(sv, data.__getattribute__(sk)))
        return new

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
        new = self.__class__()
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
            for k, v in self.__dict__.items():
                new.__setattr__(k, np.array(v[idx]))
        else:
            if isinstance(elem, int):
                index = elem
            elif isinstance(elem, (str, datetime)):
                index = np.where(self.date == Date(elem))
            for k, v in self.__dict__.items():
                new.__setattr__(k, np.array(v[index]))
        return new

    def __len__(self) -> int:
        for e in self.__dict__.values():
            return len(e)

    def __repr__(self) -> str:
        return repr(np.array(self.__dict__.values()))
