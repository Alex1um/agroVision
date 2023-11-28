import math

from Constants import Constants
from Constants import ConstantNotFoundException
from Data import Data
from Solar import Solar
from ResultTable import *


def hut_count(max_temps: np.ndarray, min_temps: np.ndarray):
    average_temps = (max_temps + min_temps) / 2 - constants.Tb
    return np.where(average_temps > 0, average_temps, 0)


def hui_count(hut: np.ndarray):
    cumulative_sum = np.cumsum(hut) / constants.PHU  # create array of cumulative sums
    return cumulative_sum


def huf_count(hui: np.ndarray):
    hui = hui.astype(float)
    huf = hui / (hui + np.exp(constants.ah1 - constants.ah2 * hui))
    return huf


def delta_huf_count(huf: np.ndarray):
    delta_huf = np.diff(huf)
    return np.insert(delta_huf, 0, 0)


def dh_count(hui: np.ndarray):
    mask = (hui >= constants.D_LAI)
    indices = np.where(mask)
    if len(indices[0]) > 0:
        return indices[0][0]
    return 0


def reg_count(max_temps: np.ndarray, min_temps: np.ndarray, daily_precipitation_amount: np.ndarray):
    return (np.sum(daily_precipitation_amount) * 10) / np.sum((max_temps + min_temps) / 2)


def lai_count(delta_huf: np.ndarray, hui: np.ndarray, reg: float, dh_count: int):
    lai = [0]
    for i in range(1, dh_count + 1):
        delta_lai = delta_huf[i] * constants.LAImx * (1 - math.exp(5 * (lai[i - 1] - constants.LAImx))) * math.sqrt(reg)
        lai.append(lai[i - 1] + delta_lai)
    for j in range(dh_count + 1, len(delta_huf)):
        lai.append(lai[dh_count] * (((1 - hui[j]) / (1 - hui[dh_count])) ** constants.ad))
    return np.array(lai)


def par_count(lai: np.ndarray, solar_rad: np.ndarray):
    return 0.5 * solar_rad * (1 - np.exp(-0.65 * lai))


def vpd_count(rel_humidity: np.ndarray):
    return rel_humidity / 100


def be_CO2_count():
    return 100 * constants.CO2 / (constants.CO2 + math.exp(constants.bc1 - constants.bc2 * constants.CO2))


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
    # можно задать 3 параметром, куда сохранять результирующий xl
    table = ResultTable("excels/Таблица вычислений_НСО_районы.xlsx", "excels/Перечень_район_метеостанция.xlsx")
    # переменные итерирования(ниже): (имена файлов(не пути!)), (дата начала, дата конца), (индексы урожайности(HI)), ("Что должно получиться по факту", индексы) - как в xl
    for (meteo_file_name, solar_file_name), (date_start, date_end), HI, res_values in table.iter():
        meteo_file_path_1 = table.find_path_in_dir("1_первая часть сезона",
                                                   meteo_file_name)  # получаем полный путь, из которого создавать класс.
        solar_file_path_1 = table.find_path_in_dir("1_первая часть сезона",
                                                   solar_file_name)
        meteo_file_path_2 = table.find_path_in_dir("2_вторая часть сезона",
                                                   meteo_file_name)  # получаем полный путь, из которого создавать класс.
        solar_file_path_2 = table.find_path_in_dir("2_вторая часть сезона",
                                                   solar_file_name)  # Параметры: путь до папки, в которой искать, имя файла

        data: Data = Data.from_file(meteo_file_path_1)
        data2: Data = Data.from_file(meteo_file_path_2)
        full_data = data + data2
        data = full_data[date_start:]

        solar: Solar = Solar.from_file(solar_file_path_1)
        solar2: Solar = Solar.from_file(solar_file_path_2)
        solar += solar2
        solar = solar[date_start:]

        hut = hut_count(data.Tmax, data.Tmin)

        hui = hui_count(hut)

        huf = huf_count(hui)

        delta_huf = delta_huf_count(huf)

        dh: int = dh_count(hui)

        mid_date = data2.date[0].date
        mid_data = full_data[:mid_date]
        reg: float = reg_count(mid_data.Tmax, mid_data.Tmin, mid_data.daily_precipitation_amount)

        lai = lai_count(delta_huf, hui, reg, dh)

        par = par_count(lai, solar.radiation)

        vpd = vpd_count(data.rel_humidity)

        be_CO2: float = be_CO2_count()

        be = be_count(vpd, be_CO2)

        delta_bp = delta_bp_count(be, par)

        delta_b = delta_b_count(delta_bp, reg)

        biom = biom_count(delta_b)

        result = result_count(biom)

        print(meteo_file_name, solar_file_name, date_start, mid_date, len(data.Tmax), result, np.max(biom))
        #print(result * HI[0] * 10, result * HI[1] * 10, result * HI[2] * 10)

        table.set_current_row((result * HI[0] * 10, result * HI[1] * 10, result * HI[2] * 10))
        # Запись в Прогноз (индекс 1, индекс 2, индекс 1). Можно использовать любой итератор(list/tuple/np.array)
        # записывать можно только во время итерации, иначе не работает


if __name__ == '__main__':
    try:
        constants = Constants("./excels/constant_raion.xlsx")
    except ConstantNotFoundException:
        exit(1)
    main()
