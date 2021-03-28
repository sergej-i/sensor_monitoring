''' мониторинг процессов: слушаем датчики.
процессы датчиков поднимаются автоматом, если они не были выключены пользователем '''

from subprocess import Popen
from threading import Thread
from time import sleep
from queue import Queue, Empty

from lib.monitoring_config import SensorsConfig

# команды позоляющие выйти из программы
_exit_commands = ['exit', 'quit', 'q']

def user_input_check():
    ''' ввёл ли пользователь команду? какую? '''
    user_input = ''
    try:
        user_input = q.get(block=False)
        print(f'command: {user_input}')
    except Empty:
        pass
    return user_input.strip()

def user_input_get():
    ''' для взятия комманд пользователя из параллельного потока '''
    global q
    global _exit_commands
    data = ''
    print('Ожидаю комманд')
    print('-' * 20)
    while data not in _exit_commands:
        data = input()
        print(f'command echo: {data}')
        q.put(data)
    return data

def sensor_run_check(sensor):
    ''' процесс датчика работает? '''
    pop = sensor['popen']
    if pop and pop.poll() is None:
        return True
    return False

if __name__ == '__main__':
    # считываем конфигурацию
    config = SensorsConfig()

    if not config.sensors:
        exit(1)

    # для ввода комманд пользователем
    q = Queue()

    print('''
    Доступны комманды:\n
    "(q)uit" - выйти из программы\n
    "(l)ist" - список датчиков\n
    "(t)erm <sensor name>" - остановить работу датчика\n
    "(s)tart <sensor name>" - возобновить работу датчика\n
    "(p)rint <sensor name>" - вывести последние показания датчика (log)\n
    ''')

    # поток для ожидания комманд пользователя
    input_thread = Thread(target=user_input_get)
    input_thread.start()

    # процессы читающие данчики
    for _, v in config.sensors_dict.items():
        if v['autoload']:
            v['popen'] = Popen(v['run'])
            v['up'] = True
            print(f'Датчик {v["name"]} активирован (autoload)')
        else:
            v['popen'] = None
            v['up'] = False
        # 1 - если пользователь отключил (статус)
        v['off_by_user'] = 0

    # слушаем датчики и команды пользователя
    while True:
        sleep(1)
        user_input = user_input_check()
        if user_input:
            command = user_input.split()

            # список датчиков
            if command[0] == 'list' or command[0] == 'l':
                config.print_sensors()

            # выход из программы
            elif command[0] in _exit_commands:
                for _, v in config.sensors_dict.items():
                    pop = v['popen']
                    if pop and pop.poll() is None:
                        pop.terminate()
                print('bye!')
                break

            # остановка атчика
            elif len(command) == 2 and command[0] == 'term' or command[0] == 't':
                if command[1] in config.sensors_names:
                    sensor_term = config.sensors_dict[command[1]]
                    if not sensor_run_check(sensor_term):
                        print(f'Датчик {command[1]} уже не работает')
                    else:
                        sensor_start['popen'].terminate()
                        sensor_start['popen'].wait()
                        print(f'Датчик {command[1]} остановлен')
                    sensor_term['up'] = False
                    sensor_term['off_by_user'] = True
                    sensor_term['autorestart'] = False

            # включение атчика
            elif len(command) == 2 and command[0] == 'start' or command[0] == 's':
                if command[1] in config.sensors_names:
                    sensor_start = config.sensors_dict[command[1]]
                    if sensor_run_check(sensor_start):
                        print(f'Датчик {command[1]} уже работает')
                    else:
                        sensor_start['popen'] = Popen(sensor_start['run'])
                        print(f'Датчик {command[1]} запущен')
                    sensor_start['up'] = True
                    sensor_start['off_by_user'] = False

            # лог датчика
            elif len(command) == 2 and command[0] == 'print' or command[0] == 'p':
                if command[1] in config.sensors_names:
                    [print(x) for x in config.sensor_log_short_get(command[1])]

            else:
                print('неизвестная команда (для выхода наберите "q" или "quit")')

        for _, v in config.sensors_dict.items():
            # if v['up']:
            pop = v['popen']
            if pop:
                code = pop.poll()
                if code is not None:
                    if v['up']:
                        print(f'Датчик {v["name"]} не работает, code={code}')
                        v['up'] = False
                    if v['autorestart'] and not v['off_by_user']:
                        v['popen'] = Popen(v['run'])
                        v['up'] = True
                        print(f'Возоблена работа датчика {v["name"]} (autorestart)')

    # и команды больше не нужно от пользователя ждать
    input_thread.join()
