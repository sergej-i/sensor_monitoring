''' Эмулятор процесса чтения некоторого значения датчика/сенсора
процесс НЕ упадёт при неверном значении датчика '''

from random import randint
from time import sleep
from .sensor import Sensor, SensorException

class SensorDemo2(Sensor):
    ''' "Странно работающий" сенсор '''
    SENSOR_PRINT_NAME = 'SENSOR 2'
    # пусть датчик выдаёт значения от SENSOR_MIN_VAL до SENSOR_MAX_VAL
    SENSOR_MIN_VAL = -100
    SENSOR_MAX_VAL = 100

    def get_val(self, debug_mode=False):
        ''' чтение значения сенсора '''
        # эмулируем выход за диапазон
        sensor_reading = randint(
            SensorDemo2.SENSOR_MIN_VAL - abs(SensorDemo2.SENSOR_MIN_VAL) // 10,
            SensorDemo2.SENSOR_MAX_VAL + abs(SensorDemo2.SENSOR_MAX_VAL) // 10
        )
        if (sensor_reading < SensorDemo2.SENSOR_MIN_VAL
                or sensor_reading > SensorDemo2.SENSOR_MAX_VAL):
            try:
                raise SensorException(
                    f'{SensorDemo2.SENSOR_PRINT_NAME}: '
                    'выход значений датчика из допустимого интервала'
                )
            except SensorException:
                self.log.exception(
                    'Sensor reading error',
                    extra={SensorDemo2.LOG_VAL_FIELD: sensor_reading}
                )
        else:
            self.log.info('Sensor reading', extra={SensorDemo2.LOG_VAL_FIELD: sensor_reading})
        # для получения значения датчика нужно 2сек
        waiting_time = 2
        if debug_mode:
            print(SensorDemo2.SENSOR_PRINT_NAME, sensor_reading)
        sleep(waiting_time)
        return sensor_reading
