import logging
import logging.config

logging.config.fileConfig("logging.conf")

root_logger = logging.getLogger()
meteo_logger = logging.getLogger("meteo")
solar_logger = logging.getLogger("solar")
