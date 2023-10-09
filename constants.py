import pandas as pd


class Constants:
    def __init__(self):
        constant_dict = {}
        df = pd.read_excel('./constants/constant_raion.xlsx')
        for index, row in df.iterrows():
            key = row['Обозначение']
            value = row['Значение']
            constant_dict[key] = value

        self.constant_dict = constant_dict