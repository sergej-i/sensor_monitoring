''' Считывание конфигурации о датчиках '''

import os
import json
import sqlite3
from jsonschema import validate, ValidationError
from .sqlite_sensor_logging import SQLiteSensorHandler

class MonitoringConfig:
    ''' конфигуратор датчиков '''

    config_err_msg = 'Ошибка в конфиг файле: '

    def load(self):
        ''' считываем конфиг из json-файла '''
        fname = os.path.join(self.conf_path, 'monitoring.json')
        sname = os.path.join(self.conf_path, 'monitoring.schema.json')
        loaded_config = None
        try:
            with open(fname, 'r') as f:
                loaded_config = json.load(f)
            with open(sname, 'r') as f:
                config_schema = json.load(f)
            validate(instance=loaded_config, schema=config_schema)
            # if validation is success only
            return loaded_config
        except OSError as e:
            print("Нельзя открыть файл конфигурации (существует?, права доступа?):", fname)
        except json.JSONDecodeError as e:
            print(MonitoringConfig.config_err_msg, e)
        except ValidationError as e:
            print(MonitoringConfig.config_err_msg, e)
        return None

    def _sensors_get(self):
        ''' прочитать раздел с сенсорами '''
        try:
            sensors = self.config['monitoring_config']['sensors']
            if isinstance(sensors, list):
                return sensors
        except KeyError as e:
            print(MonitoringConfig.config_err_msg, 'KeyError', e)
        return None

    @staticmethod
    def _sensor_load(sensor_config_obj):
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
            print(MonitoringConfig.config_err_msg, 'KeyError', e)
        return None

    def __init__(self, conf_path=''):
        self.conf_path = conf_path or 'sensor_monitoring_config'
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
            for sensor in self.sensors:
                print(indent, sensor['name'])


if __name__ == '__main__':
    config = MonitoringConfig()
    print(config.config)
    print(config.sensors_dict)
    