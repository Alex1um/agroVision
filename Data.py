import openpyxl
import numpy as np
import csv
from openpyxl.utils.exceptions import InvalidFileException
from datetime import datetime
from Date import Date
from NpAnnotBase import NpAnnotBase
from loggers import meteo_logger


class Data(NpAnnotBase):
    name: str
    lat: float
    long: float
    date: Date
    Tmax: float
    Tmin: float
    daily_precipitation_amount: float
    rel_humidity: float
    avg_wind_speed: float

    @classmethod
    def from_file(self, file_path: str):
        # Assuming file is xl
        parsed_total = 0
        warnings = 0
        successful = 0
        errors = 0
        xl = True
        self = self()
        try:
            xl = openpyxl.open(file_path)
            page = xl.active
            # iterate over annotations and readed from xl cols. NOTE: Assuming annotations and columns are in the same order
            for col_i, ((k, tpe), readed) in enumerate(
                zip(
                    self.__annotations__.items(),
                    page.iter_cols(0, len(self.__annotations__), values_only=True),
                )
            ):
                # vectorize type for faster type conversions
                np_func = np.vectorize(tpe)
                # set attribute to readed array, converted to annotation type
                try:
                    np_converted = np_func(np.array(readed))
                    ln = len(np_converted)
                    if ln > parsed_total:
                        parsed_total = ln
                    if successful == 0 or ln < successful:
                        successful = ln
                    self.__setattr__(k, np_converted)
                except Exception as e:
                    meteo_logger.error(
                        f"{file_path} - Error occupied while type convertation in column {col_i}: {e}"
                    )
        except InvalidFileException as ie:
            meteo_logger.debug(
                f"{file_path} - file is not a xl file(exception: {ie}). Trying to parse as csv..."
            )
            xl = False
        except Exception as e:
            meteo_logger.error(
                f"{file_path} - Exception {e} occuped while parsing xl file"
            )
        if not xl:
            try:
                with open(file_path, "r") as f:
                    readed = csv.reader(f)
                    parsed = list()
                    param_count = len(self.__annotations__)
                    # iterate over rows
                    for row_i, row in enumerate(readed):
                        try:
                            # check if not empty
                            if row:
                                # prealloc list
                                parsed_row = list()
                                # iterate over values in row
                                for val, (name, type) in zip(
                                    row, self.__annotations__.items()
                                ):
                                    # check tabs and strip
                                    if "\t" * 5 in val:
                                        dbg = val[: val.find("\t")]
                                        meteo_logger.warning(
                                            f"{file_path} - found tabs in '{row_i}' at '{val}'. truncated to {dbg}"
                                        )
                                        warnings += 1
                                        val = dbg
                                    try:
                                        # convert readed value and add to current (col_name) attribute list
                                        parsed_row.append(type(val))
                                    except Exception as e:
                                        # NOTE: Skipping non-convertible lines
                                        meteo_logger.warning(
                                            f"{file_path} - Exception {e} occupied while parsing {val} to {name} at {row_i} row. Skipping row..."
                                        )
                                        warnings += 1
                                        break
                                else:
                                    parsed_count = len(parsed_row)
                                    if parsed_count == param_count:
                                        parsed.append(parsed_row)
                                        successful += 1
                                    else:
                                        meteo_logger.warning(
                                            f"{file_path} - Parsed not enough params: {parsed_count} != {param_count} at row {row_i}"
                                        )
                                        warnings += 1
                            else:
                                meteo_logger.warning(
                                    f"{file_path} - Row {row_i} is empty"
                                )
                                warnings += 1
                        except Exception as e:
                            meteo_logger.error(
                                "{file_path} - Error occupied while parsing row {row_i}: {e}"
                            )
                            errors += 1
                            break
                    else:
                        parsed_total = row_i + 1
                    parsed = np.transpose(np.array(parsed))
                    # convert attribute lists to np.array
                    for k, v in zip(self.__annotations__.keys(), parsed):
                        self.__setattr__(k, v)
            except Exception as e:
                meteo_logger.error(
                    "{file_path} - Error occupied while parsing csv file: {e}"
                )
        meteo_logger.info(
            f"{file_path} - Successfully parsed {successful} rows of {parsed_total} total. Errors: {errors}, Warnings: {warnings}"
        )
        return self


if __name__ == "__main__":
    # print(Data("./meteo_data/BAGAN.csv"))
    # print(Data("./1_первая часть сезона/метео/BAGAN"))
    # print(Data("./combined/BAGAN.csv").__dict__)
    d = Data.from_file("1_первая часть сезона/метео/BAGAN")
    d1 = Data.from_file("1_первая часть сезона/метео/BAGAN")
    d2 = Data.from_file("2_вторая часть сезона/метео/BAGAN.xlsx")
    print(d[1].date)
    print(d["2022/05/05":"2022/05/17"].date)
    print(d["2022/05/25":].date)
    print(len(d1))
    print(len(d2))
    print(len(d1 + d2))
    # import glob
    # for f1, f2 in zip(
    #     sorted(glob.glob("1_первая часть сезона/метео/*"), key=lambda x: x.split("/")[-1]),
    #     sorted(glob.glob("2_вторая часть сезона/метео/*"), key=lambda x: x.split("/")[-1])
    #     ):
    #     name = f1.split("/")[-1]
    #     print(f1, f2)
    #     d1 = Data(f1)
    #     d2 = Data(f2)
    #     # print(d2)
    #     d1.append(d2)
    #     d1.to_csv(f"combined/{name}.csv")
