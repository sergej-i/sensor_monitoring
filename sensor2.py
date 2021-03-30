''' Эмулятор процесса чтения некоторого значения датчика/сенсора
процесс НЕ упадёт при неверном значении датчика '''

import os
from sensor_monitoring import SensorDemo2

if __name__ == '__main__':
    print(f'{SensorDemo2.SENSOR_PRINT_NAME}: PID={os.getpid()}')
    # TODO config
    sensor2 = SensorDemo2('sensors.sqlite', 'sensor2_log')
    while True:
        sensor2_val = sensor2.get_val(debug_mode=True)
