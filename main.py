import csv
from constants import Constants
import pandas as pd

# def hut_count(data):
#     for dict in data:


if __name__ == '__main__':
    constants = Constants()
   # print(constants.constant_dict)

    bagan_data = []
    headers = ["name", "latitude", "longitude", "date", "max_temp", "min_temp", "rain", "humidity", "wind_speed"]

    with open('./meteo_data/BAGAN.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            row_dict = {headers[i]: row[i] for i in range(len(headers))}
            bagan_data.append(row_dict)

    # print(*bagan_data, sep='\n')
