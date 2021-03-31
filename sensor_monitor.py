#!python
''' мониторинг процессов: слушаем датчики.
процессы датчиков поднимаются автоматом, если они не были выключены пользователем '''

import os
from sensor_monitoring import SensorsMonitor

conf_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(conf_path)
conf_path = os.path.join(conf_path, 'sensor_monitoring_config')
monitor = SensorsMonitor(conf_path=conf_path)
monitor.main()
