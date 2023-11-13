import math

import numpy as np
from constants import Constants
from constants import ConstantNotFoundException
from data import Data
from solar import Solar


# TODO: fix start date of count from Таблица вычислений_НСО_районы_2022.xlsx


# Checked with simple
def hut_count(max_temps: np.ndarray, min_temps: np.ndarray):
    average_temps = (max_temps + min_temps) / 2 - constants.Tb
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
    hui = hui.astype(float)
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
    return np.insert(delta_huf, 0, 0)


# def delta_huf_count_simple(huf: np.ndarray):
#     delta_huf = []
#     for i in range(len(huf) - 1):
#         delta_huf.append(huf[i + 1] - huf[i])
#     return delta_huf

# def dh_count_simple(hui: np.ndarray):
#     for i in range(len(hui) - 1):
#         if hui[i] >= constants.D_LAI:
#             return i
#     return 0

def dh_count(hui: np.ndarray):
    mask = hui >= constants.D_LAI
    indices = np.where(mask)
    if len(indices[0]) > 0:
        return indices[0][0]
    return 0


def reg_count(max_temps: np.ndarray, min_temps: np.ndarray, daily_precipitation_amount: np.ndarray, aging: int):
    # print("avg temps: ", (max_temps[:aging] + min_temps[:aging]) / 2)
    # print("rain: ", daily_precipitation_amount[:aging])
    return (np.sum(daily_precipitation_amount[:aging]) * 10) / np.sum((max_temps[:aging] + min_temps[:aging]) / 2)


def lai_count(delta_huf: np.ndarray, hui: np.ndarray, reg: float, dh_count: int):
    lai = [0]
    for i in range(1, dh_count + 1):
        lai.append(lai[i - 1] + delta_huf[i] * constants.LAImx * (
                1 - math.exp(5 * (lai[i - 1] - constants.LAImx))) * math.sqrt(reg))
    for j in range(dh_count + 1, len(delta_huf)):
        lai.append(lai[dh_count] * (((1 - hui[j]) / (1 - hui[dh_count])) ** constants.ad))
    return np.array(lai)


def par_count(lai: np.ndarray, solar_rad_first: np.ndarray, solar_rad_second: np.ndarray):
    solar_rad = np.concatenate((solar_rad_first, solar_rad_second))
    return 0.5 * solar_rad * (1 - np.exp(-0.65 * lai))


def vpd_count(rel_humidity: np.ndarray):
    return rel_humidity / 100


def be_CO2_count():
    return 100 * constants.СО2 / (constants.СО2 + math.exp(constants.bc1 - constants.bc2 * constants.СО2))


def be_count(vpd: np.ndarray, be_CO2: float):
    return np.where(vpd > 0.5, be_CO2 - constants.bc3 * (vpd - 1), 0)


def delta_bp_count(be: np.ndarray, par: np.ndarray):
    return 0.001 * be * par


def delta_b_count(delta_bp: np.ndarray, reg: float):
    return delta_bp * reg


def biom_count(delta_b: np.ndarray):
    return np.cumsum(delta_b)


def result_count(biom: np.ndarray):
    return np.max(biom) * 0.4169 + 2.7455


def main():
    data = Data("1_первая часть сезона/метео/TOGUCHI")
    data2 = Data("2_вторая часть сезона/метео/TOGUCHI.xlsx")
    data.append(data2)

    solar1 = Solar("1_первая часть сезона/солнечная радиация/sun_toguchi")
    solar2 = Solar("2_вторая часть сезона/солнечная радиация/sun_toguchi.xlsx")

    # data.trim("05/05/2023")
    hut = hut_count(data.Tmax, data.Tmin)
    # print("hut:", hut)
    hui = hui_count(hut)
    # print("hui:", hui)
    huf = huf_count(hui)
    # print("huf:", ["{:.6f}".format(item) for item in huf])
    delta_huf = delta_huf_count(huf)
    # print("delta huf:", ["{:.6f}".format(item) for item in delta_huf])
    dh: int = dh_count(hui)
    # print("dh: ", dh)
    reg: float = reg_count(data.Tmax, data.Tmin, data.daily_precipitation_amount, 78)
    # print("reg: ", reg)

    lai = lai_count(delta_huf, hui, reg, dh)
    # print("lai:", ["{:.6f}".format(item) for item in lai])

    par = par_count(lai, solar1.radiation, solar2.radiation)
    # print("par:", ["{:.6f}".format(item) for item in par])

    vpd = vpd_count(data.rel_humidity)

    be_CO2: float = be_CO2_count()
    # print(be_CO2)
    be = be_count(vpd, be_CO2)
    # print("be:", ["{:.6f}".format(item) for item in be])

    delta_bp = delta_bp_count(be, par)
    # print("delta_bp:", ["{:.6f}".format(item) for item in delta_bp])
    delta_b = delta_b_count(delta_bp, reg)
    # print("delta_b:", ["{:.6f}".format(item) for item in delta_b])
    biom = biom_count(delta_b)
    result = result_count(biom)
    print(result)


if __name__ == '__main__':
    try:
        constants = Constants("./excels/constant_raion.xlsx")
    except ConstantNotFoundException:
        exit(1)
    main()
