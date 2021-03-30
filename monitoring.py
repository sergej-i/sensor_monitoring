''' мониторинг процессов: слушаем датчики.
процессы датчиков поднимаются автоматом, если они не были выключены пользователем '''

from sensor_monitoring import SensorsMonitor

monitor = SensorsMonitor()
monitor.main()
