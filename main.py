import csv
from constants import Constants
from constants import ConstantNotFoundException


# TODO: fix start date of count from excel file
def hut_count(data):
    hut = []
    for dict in data:
        average_temp = (float(dict["max_temp"]) + float(dict["min_temp"])) / 2 - getattr(constants, "Tb")
        hut.append(average_temp if average_temp > 0 else 0)
    return hut


def hui_count(hut):
    hui = []
    for i in range(len(hut)):
        hui.append(sum(hut[0:i]) / getattr(constants, "PHU"))
    return hui


def main():
    bagan_data = []
    headers = ["name", "latitude", "longitude", "date", "max_temp", "min_temp", "rain", "humidity", "wind_speed"]

    with open('./meteo_data/BAGAN.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            row_dict = {headers[i]: row[i] for i in range(len(headers))}
            bagan_data.append(row_dict)

    hut = hut_count(bagan_data)
    hui = hui_count(hut)
    print(hui)
    print(len(hui))


if __name__ == '__main__':
    try:
        constants = Constants()
    except ConstantNotFoundException:
        exit(1)

    main()
