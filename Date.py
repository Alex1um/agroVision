from datetime import datetime

class Date:

    def __init__(self, date: str | datetime, year=2022) -> None:
        if isinstance(date, datetime):
            self.date = date
        elif isinstance(date, str):
            self.date = datetime.strptime(date, "%Y/%m/%d")
        elif isinstance(date, Date):
            self.date = date.date
        elif isinstance(date, float):
            d, m = divmod(date, 1)
            m = int(round(m, 2) * 100)
            d = int(d)
            self.date = datetime(year, m, d)
        else:
            raise ValueError(f"Cannot parse date from {date} of type {type(date)}")
    
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
