import pandas as pd


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

    def __init__(self):
        constant_dict = {}
        df = pd.read_excel('./constants/constant_raion.xlsx')
        for index, row in df.iterrows():
            key = row['Обозначение']
            value = row['Значение']
            constant_dict[key] = float(value)

            # print(constant_dict)
            # self.constant_dict = constant_dict

        constants_to_check = ["D_LAI", "HI", "HMX", "LAImx", "PHU", "RDMX", "SNk", "Tb", "Topt", "ad", "СО2", "ah1",
                              "ah2", "bc1", "bc2", "bc3"]
        #  Constants.__dict__["__annotations__"].keys()
        for const in Constants.__dict__["__annotations__"].keys():
            value = constant_dict.get(const)
            if value is not None:
                setattr(self, const, value)
            else:
                print(f"Константа '{const}' не найдена в таблице констант.")
                raise ConstantNotFoundException("Const not found")
