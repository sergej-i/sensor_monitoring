''' мониторинг процессов: слушаем датчики.
процессы датчиков поднимаются автоматом, если они не были выключены пользователем '''

import sys
from subprocess import Popen
from threading import Thread
from time import sleep
from queue import Queue, Empty

from .monitoring_config import MonitoringConfig


class SensorsMonitor:
    ''' Мониторинг процессов опроса датчиков '''
    # команды позоляющие выйти из программы
    _EXIT_COMMANDS = ['exit', 'quit', 'q']

    def __init__(self, conf_path=''):
        # считываем конфигурацию
        self.config = MonitoringConfig(conf_path)
        # ошибки в конфиге
        if not self.config.sensors:
            sys.exit(1)

        print('''
        Доступны комманды:\n
        "(q)uit" - выйти из программы\n
        "(l)ist" - список датчиков\n
        "(t)erm <sensor name>" - остановить работу датчика\n
        "(s)tart <sensor name>" - возобновить работу датчика\n
        "(p)rint <sensor name>" - вывести последние показания датчика (log)\n
        ''')

    @staticmethod
    def user_input_check(commands_queue):
        ''' ввёл ли пользователь команду? какую? '''
        user_input = ''
        try:
            user_input = commands_queue.get(block=False)
            print(f'command: {user_input}')
        except Empty:
            pass
        return user_input.strip()

    @staticmethod
    def user_input_get(commands_queue):
        ''' для взятия комманд пользователя из параллельного потока '''
        data = ''
        print('Ожидаю комманд')
        print('-' * 20)
        while data not in SensorsMonitor._EXIT_COMMANDS:
            data = input()
            print(f'command echo: {data}')
            commands_queue.put(data)
        return data

    @staticmethod
    def sensor_run_check(sensor):
        ''' процесс датчика работает? '''
        if sensor['popen'] and sensor['popen'].poll() is None:
            return True
        return False

    def autoload(self):
        ''' поднимаем процессы чтения датчиков, если у них стоит флаг autoload '''
        # процессы читающие данчики
        for _, v in self.config.sensors_dict.items():
            if v['autoload']:
                v['popen'] = Popen(v['run'])
                v['up'] = True
                print(f'Датчик {v["name"]} активирован (autoload)')
            else:
                v['popen'] = None
                v['up'] = False
            # 1 - если пользователь отключил (статус)
            v['off_by_user'] = 0

    def list_sensors(self, command):
        ''' список датчиков '''
        if command[0] == 'list' or command[0] == 'l':
            self.config.print_sensors()
            return True
        return False


    def exit_loop(self, command):
        ''' пользователь ввёл команду для выхода '''
        if command[0] in SensorsMonitor._EXIT_COMMANDS:
            for _, v in self.config.sensors_dict.items():
                if v['popen'] and v['popen'].poll() is None:
                    v['popen'].terminate()
            print('bye!')
            return True
        return False

    def terminate_sensor(self, command):
        ''' остановка датчика '''
        if len(command) == 2 and command[0] == 'term' or command[0] == 't':
            if command[1] in self.config.sensors_names:
                sensor_term = self.config.sensors_dict[command[1]]
                if not self.sensor_run_check(sensor_term):
                    print(f'Датчик {command[1]} уже не работает')
                else:
                    sensor_term['popen'].terminate()
                    sensor_term['popen'].wait()
                    print(f'Датчик {command[1]} остановлен')
                sensor_term['up'] = False
                sensor_term['off_by_user'] = True
                sensor_term['autorestart'] = False
                return True
            print('Датчика с таким названием нет:', command[1])
        return False

    def start_sensor(self, command):
        ''' включение атчика '''
        if len(command) == 2 and command[0] == 'start' or command[0] == 's':
            if command[1] in self.config.sensors_names:
                sensor_start = self.config.sensors_dict[command[1]]
                if self.sensor_run_check(sensor_start):
                    print(f'Датчик {command[1]} уже работает')
                else:
                    sensor_start['popen'] = Popen(sensor_start['run'])
                    print(f'Датчик {command[1]} запущен')
                sensor_start['up'] = True
                sensor_start['off_by_user'] = False
                return True
            print('Датчика с таким названием нет:', command[1])
        return False

    def sensor_log_show(self, command):
        ''' лог датчика '''
        if len(command) == 2 and command[0] == 'print' or command[0] == 'p':
            if command[1] in self.config.sensors_names:
                for i in self.config.sensor_log_short_get(command[1]):
                    print(i)
                return True
            print('Датчика с таким названием нет:', command[1])
        return False

    def check_sensors_processes(self):
        ''' проверка, что никакой процесс опроса датчиков не упал '''
        for _, v in self.config.sensors_dict.items():
            if v['popen']:
                code = v['popen'].poll()
                if code is not None:
                    if v['up']:
                        print(f'Датчик {v["name"]} не работает, code={code}')
                        v['up'] = False
                    if v['autorestart'] and not v['off_by_user']:
                        v['popen'] = Popen(v['run'])
                        v['up'] = True
                        print(f'Возоблена работа датчика {v["name"]} (autorestart)')


    def main(self):
        ''' main loop '''
        # поток для ожидания комманд пользователя
        commands_q = Queue()
        input_thread = Thread(target=self.user_input_get, args=(commands_q,))
        input_thread.start()

        self.autoload()
        while True:
            sleep(1)

            self.check_sensors_processes()

            user_input_ = self.user_input_check(commands_q)
            if user_input_:
                command = user_input_.split()
                if self.list_sensors(command):
                    continue
                if self.terminate_sensor(command):
                    continue
                if self.start_sensor(command):
                    continue
                if self.sensor_log_show(command):
                    continue
                if self.exit_loop(command):
                    break
                print('неизвестная команда (для выхода наберите "q" или "quit")')

        # и команды больше не нужно от пользователя ждать
        input_thread.join()


if __name__ == '__main__':

    monitor = SensorsMonitor()
    monitor.main()
