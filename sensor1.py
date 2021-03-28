''' Эмулятор процесса чтения некоторого значения датчика/сенсора
процесс упадёт при неверном значении датчика '''

import os
import logging
from random import randint
from time import sleep
import sqlite3
from lib.sensor import Sensor, SensorException

class Sensor1(Sensor):
    ''' "Странно работающий" сенсор '''

    # пусть датчик выдаёт значения от 0 до SENSOR_MAX_VAL
    # но не все значения валидны
    SENSOR_MAX_VAL = 11 * 9
    # будем считать, что данные значения исправный сенсор отправить не может
    SENSOR_VALS_FOR_EXCEPTION = [x * 11 for x in range((SENSOR_MAX_VAL + 1) // 10)]

    def get_val(self, debug_mode=False):
        ''' чтение значения сенсора '''
        sensor_reading = randint(0, Sensor1.SENSOR_MAX_VAL)
        if sensor_reading in Sensor1.SENSOR_VALS_FOR_EXCEPTION:
            self.log.error('Sensor reading error', extra={Sensor1.LOG_VAL_FIELD: sensor_reading})
            raise SensorException('SENSOR 1: out of order')
        else:
            self.log.info('sensor reading', extra={Sensor1.LOG_VAL_FIELD: sensor_reading})
        # сенсор нестабилен в отдаче показаний по времени
        waiting_time = sensor_reading % 5 + 1
        if debug_mode:
            print('SENSOR 1', sensor_reading)
        sleep(waiting_time)
        return sensor_reading

if __name__ == '__main__':
    print(f'SENSOR 1: PID={os.getpid()}')

    # TODO config
    sensor1 = Sensor1('sensors.sqlite', 'sensor1_log')
    while True:
        sensor1_val = sensor1.get_val(debug_mode=True)
