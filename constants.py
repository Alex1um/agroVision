import pandas as pd


class ConstantNotFoundException(Exception):
    pass


class Constants:
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

        for const in constants_to_check:
            value = constant_dict.get(const)
            if value is not None:
                setattr(self, const, value)
            else:
                print(f"Константа '{const}' не найдена в таблице констант.")
                raise ConstantNotFoundException("Const not found")
