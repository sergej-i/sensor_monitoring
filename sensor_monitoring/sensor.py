''' Эмулятор процесса чтения некоторого значения датчика/сенсора '''

import logging
import sqlite3
from .sqlite_sensor_logging import SQLiteSensorHandler

# процесс чтения может попасть в "исключительную ситуацию"
class SensorException(Exception):
    ''' Датчик неисправен '''

class Sensor:
    ''' Заготовка сенсора '''
    LOG_VAL_FIELD = SQLiteSensorHandler.LOG_VAL_FIELD

    def __init__(self, log_dbname, log_tablename):
        self.log_tablename = log_tablename
        self.conn = sqlite3.connect(log_dbname)
        sqlite_handler = SQLiteSensorHandler(log_dbname, log_tablename)
        self.log = logging.getLogger('')
        self.log.addHandler(sqlite_handler)
        self.log.setLevel('DEBUG')  # TODO config

    def get_val(self, debug_mode=False):
        ''' чтение значения сенсора '''
        raise NotImplementedError

if __name__ == '__main__':
    sensor = Sensor('sensor_test.sqlite', 'sensor_log')
    sensor.get_val()
