import openpyxl
import logging


class ConstantNotFoundException(Exception):
    pass


class Constants:
    D_LAI: float
    HI: float #three values from Таблица вычислений_НСО_районы_2022.xlsx
    HMX: float
    LAImx: float
    PHU: float
    RDMX: float
    SNk: float
    Tb: float
    Topt: float
    ad: float
    СО2: float
    ah1: float
    ah2: float
    bc1: float
    bc2: float
    bc3: float

    def __init__(self, file_parh: str):
        sheet = openpyxl.open(file_parh).active
        readed_const_dict = dict(sheet.iter_rows(2, None, 2, None, values_only=True))
        logging.info(f"Считанs константs {readed_const_dict}")
        for k, v in readed_const_dict.items():
            self.__setattr__(k, v)

        not_found_constants = set(self.__annotations__.keys()) - set(readed_const_dict.keys())
        for const in not_found_constants:
            logging.error(f"Константа '{const}' не найдена в таблице констант.")
        if not_found_constants:
            raise ConstantNotFoundException("Const not found")
    
    def __repr__(self) -> str:
        return repr(vars(self))

if __name__ == "__main__":
    print(Constants("constants/constant_raion.xlsx"))
