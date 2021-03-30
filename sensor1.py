''' Эмулятор процесса чтения некоторого значения датчика/сенсора
процесс упадёт при неверном значении датчика '''

import os
from sensor_monitoring import SensorDemo1

if __name__ == '__main__':
    print(f'{SensorDemo1.SENSOR_PRINT_NAME}: PID={os.getpid()}')
    # TODO config
    sensor1 = SensorDemo1('sensors.sqlite', 'sensor1_log')
    while True:
        sensor1_val = sensor1.get_val(debug_mode=True)
