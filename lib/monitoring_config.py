''' Считывание конфигурации о датчиках '''

import json
import sqlite3
from lib.sqlite_sensor_logging import SQLiteSensorHandler
from jsonschema import validate, ValidationError

class SensorsConfig:
    ''' конфигуратор датчиков '''

    config_err_msg = 'Ошибка в конфиг файле: '

    def load(self):
        ''' считываем конфиг из json-файла '''
        fname = 'monitoring.json'
        sname = 'monitoring.schema.json'
        try:
            with open(fname, 'r') as f:
                config = json.load(f)
            with open(sname, 'r') as f:
                config_schema = json.load(f)
            validate(instance=config, schema=config_schema)
            return config
        except OSError as e:
            print("Нельзя открыть файл конфигурации (существует?, права доступа?):", fname)
        except json.JSONDecodeError as e:
            print(SensorsConfig.config_err_msg, e)
        except ValidationError as e:
            print(SensorsConfig.config_err_msg, e)

    def _sensors_get(self):
        ''' прочитать раздел с сенсорами '''
        try:
            sensors = self.config['monitoring_config']['sensors']
            if isinstance(sensors, list):
                return sensors
        except KeyError as e:
            print(SensorsConfig.config_err_msg, 'KeyError', e)

    def _sensor_load(self, sensor_config_obj):
        ''' взять конфигурацию сенсора '''
        sensor = {}
        sensor['name'] = sensor_config_obj['name']
        sensor['log_dbname'] = sensor_config_obj['log_dbname']
        sensor['log_tablename'] = sensor_config_obj['log_tablename']
        sensor['autoload'] = sensor_config_obj['autoload']
        sensor['autorestart'] = sensor_config_obj['autorestart']
        sensor['run'] = sensor_config_obj['run']
        return sensor

    def sensors_load(self, sensors_config_part):
        ''' прочитать информацию о сенсорах '''
        try:
            sensors = [self._sensor_load(s) for s in sensors_config_part]
            return sensors
        except KeyError as e:
            print(SensorsConfig.config_err_msg, 'KeyError', e)

    def __init__(self):
        self.config = self.load()
        self.sensors = []
        self.sensors_names = []
        self.sensors_dict = {}
        if self.config:
            _sensors = self._sensors_get()
            if _sensors:
                self.sensors = self.sensors_load(_sensors)
                if self.sensors:
                    self.sensors_names = [sensor['name'] for sensor in self.sensors]
                    self.sensors_dict = {sensor['name']:sensor for sensor in self.sensors}
        self.print_sensors()

    def sensor_log_get(self, sensor_name, limit=10):
        ''' не продакшн код (инъекция), только для проверки, что в логе что-то есть '''
        sensor = self.sensors_dict[sensor_name]

        conn = sqlite3.connect(sensor['log_dbname'])
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        curr.execute(f'select * from {sensor["log_tablename"]} order by created desc limit {limit}')
        return [dict(row) for row in curr.fetchall()]

    def sensor_log_short_get(self, sensor_name, limit=10):
        ''' сокращаем выборку '''
        # TODO выборка сразу нужных полей
        log = self.sensor_log_get(sensor_name, limit)
        date_fld = SQLiteSensorHandler.LOG_DATE_FIELD
        val_fld = SQLiteSensorHandler.LOG_VAL_FIELD
        rec_t_fld = SQLiteSensorHandler.LOG_REC_TYPE
        return [
            {date_fld:l[date_fld], val_fld:l[val_fld], rec_t_fld:l[rec_t_fld]} for l in log
        ]

    def print_sensors(self):
        ''' выведет названия сенсоров '''
        indent = ' ' * 3
        if self.sensors:
            print(indent, 'В конфигурации описаны следующие датчики:\n')
            [print(indent, sensor['name']) for sensor in self.sensors]


if __name__ == '__main__':
    config = SensorsConfig()
    print(config.config)
    print(config.sensors_dict)
    