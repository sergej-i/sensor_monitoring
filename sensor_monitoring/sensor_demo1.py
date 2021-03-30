''' Эмулятор процесса чтения некоторого значения датчика/сенсора
процесс упадёт при неверном значении датчика '''

from random import randint
from time import sleep
from .sensor import Sensor, SensorException

class SensorDemo1(Sensor):
    ''' "Странно работающий" сенсор '''
    SENSOR_PRINT_NAME = 'SENSOR 1'
    # пусть датчик выдаёт значения от 0 до SENSOR_MAX_VAL
    # но не все значения валидны
    SENSOR_MAX_VAL = 11 * 9
    # будем считать, что данные значения исправный сенсор отправить не может
    SENSOR_VALS_FOR_EXCEPTION = [x * 11 for x in range((SENSOR_MAX_VAL + 1) // 10)]

    def get_val(self, debug_mode=False):
        ''' чтение значения сенсора '''
        sensor_reading = randint(0, SensorDemo1.SENSOR_MAX_VAL)
        if sensor_reading in SensorDemo1.SENSOR_VALS_FOR_EXCEPTION:
            self.log.error(
                'Sensor reading error',
                extra={SensorDemo1.LOG_VAL_FIELD: sensor_reading}
            )
            raise SensorException(f'{SensorDemo1.SENSOR_PRINT_NAME}: out of order')
        self.log.info('Sensor reading', extra={SensorDemo1.LOG_VAL_FIELD: sensor_reading})
        # сенсор нестабилен в отдаче показаний по времени
        waiting_time = sensor_reading % 5 + 1
        if debug_mode:
            print(SensorDemo1.SENSOR_PRINT_NAME, sensor_reading)
        sleep(waiting_time)
        return sensor_reading
