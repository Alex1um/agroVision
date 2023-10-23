import csv
import numpy as np
from constants import Constants
from constants import ConstantNotFoundException
from data import Data

# TODO: fix start date of count from Таблица вычислений_НСО_районы_2022.xlsx


# Checked with simple
def hut_count(max_temps: np.ndarray, min_temps: np.ndarray):
    average_temps = (max_temps + min_temps) / 2 - constants.D_LAI
    return np.maximum(average_temps, 0)  # for each element if it < 0 replace with 0, else doesn't replace


# def hut_count_simple(data):
#     hut = []
#     for dict in data:
#         average_temp = (float(dict["max_temp"]) + float(dict["min_temp"])) / 2 - getattr(constants, "Tb")
#         hut.append(average_temp if average_temp > 0 else 0)
#     return hut


# Checked with simple
def hui_count(hut: np.ndarray):
    cumulative_sum = np.cumsum(hut) / constants.PHU  # create array of cumulative sums
    return cumulative_sum


# def hui_count_simple(hut):
#     hui = []
#     for i in range(len(hut)):
#         hui.append(sum(hut[0:i + 1]) / getattr(constants, "PHU"))
#     return hui


# Checked with simple
def huf_count(hui: np.ndarray):
    huf = hui / (hui + np.exp(constants.ah1 - constants.ah2 * hui))
    return huf


# def huf_count_simple(hui: np.ndarray):
#     huf = []
#     for i in hui:
#         elem = i / (i + np.exp(constants.ah1 - constants.ah2 * i))
#         huf.append(elem)
#     return np.array(huf)


# Checked with simple
def delta_huf_count(huf: np.ndarray):
    delta_huf = np.diff(huf)
    return delta_huf


# def delta_huf_count_simple(huf: np.ndarray):
#     delta_huf = []
#     for i in range(len(huf) - 1):
#         delta_huf.append(huf[i + 1] - huf[i])
#     return delta_huf


def main():

    data = Data("./meteo_data/BAGAN.csv")

    hut = hut_count(data.Tmax, data.Tmin)
    hui = hui_count(hut)
    huf = huf_count(hui)
    delta_huf = delta_huf_count(huf)  # длина будет на 1 меньше


if __name__ == '__main__':
    try:
        constants = Constants("./constants/constant_raion.xlsx")
    except ConstantNotFoundException:
        exit(1)
    main()
