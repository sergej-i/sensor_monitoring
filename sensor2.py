''' Эмулятор процесса чтения некоторого значения датчика/сенсора
процесс упадёт при неверном значении датчика '''

import os
import logging
from random import randint
from time import sleep
import sqlite3
from lib.sensor import Sensor, SensorException

class Sensor2(Sensor):
    ''' "Странно работающий" сенсор '''
    # пусть датчик выдаёт значения от SENSOR_MIN_VAL до SENSOR_MAX_VAL
    SENSOR_MIN_VAL = -100
    SENSOR_MAX_VAL = 100
    

    def get_val(self, debug_mode=False):
        ''' чтение значения сенсора '''
        # эмулируем выход за диапазон
        sensor_reading = randint(
            Sensor2.SENSOR_MIN_VAL - abs(Sensor2.SENSOR_MIN_VAL) // 10,
            Sensor2.SENSOR_MAX_VAL + abs(Sensor2.SENSOR_MAX_VAL) // 10
        )
        if sensor_reading < Sensor2.SENSOR_MIN_VAL or sensor_reading > Sensor2.SENSOR_MAX_VAL:
            try:
                raise SensorException('SENSOR 2: выход значений датчика из допустимого интервала')
            except SensorException:
                self.log.exception(
                    'Sensor reading error',
                    extra={Sensor2.LOG_VAL_FIELD: sensor_reading}
                )
        else:
            self.log.info('Sensor reading', extra={Sensor2.LOG_VAL_FIELD: sensor_reading})
        # для получения значения датчика нужно 2сек
        waiting_time = 2
        if debug_mode:
            print('SENSOR 2', sensor_reading)
        sleep(waiting_time)
        return sensor_reading

if __name__ == '__main__':
    print(f'SENSOR 2: PID={os.getpid()}')

    # TODO config
    Sensor2 = Sensor2('sensors.sqlite', 'sensor2_log')
    while True:
        Sensor2_val = Sensor2.get_val(debug_mode=True)
