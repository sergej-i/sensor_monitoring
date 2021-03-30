''' Handler SQLite для logging '''

import sqlite3
import logging
import time

class SQLiteHandler(logging.Handler):
    """ Handler SQLite для logging """

    LOG_DATE_FIELD = 'asctime'
    LOG_REC_TYPE = 'levelname'

    @classmethod
    def _get_logrecord_attributes(cls):
        # атрибуты на основе
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        # IMPORTANT! без поля created сложно представить лог (=> обязательно должно быть)
        return {
            'args': 'text', 'asctime': 'text', 'created': 'numeric', 'exc_info': 'text',
            'filename': 'text', 'funcName': 'text', 'levelname': 'text', 'levelno': 'int',
            'lineno': 'int', 'message': 'text', 'module': 'text', 'msecs': 'numeric',
            'msg': 'text', 'name': 'text', 'pathname': 'text', 'process': 'int',
            'processName': 'text', 'relativeCreated': 'numeric', 'stack_info': 'text',
            'thread': 'int', 'threadName': 'text'
        }

    def _get_create_tab_sql(self):
        ''' сборка SQL для создания таблицы с логом '''
        columns_def = [f'{k} {v}, ' for k, v in self._get_logrecord_attributes().items()]
        columns_defs = ''.join(columns_def)[:-2]
        return f'CREATE TABLE IF NOT EXISTS {self._log_table_name}({columns_defs})'

    def _get_insert_sql(self):
        ''' сборка SQL для вставки записи в лог '''
        columns = [f'{col}, ' for col in sorted(self._get_logrecord_attributes().keys())]
        columns_str = ''.join(columns)[:-2]
        binds = [f':{col}, ' for col in sorted(self._get_logrecord_attributes().keys())]
        binds_str = ''.join(binds)[:-2]
        return f'INSERT INTO {self._log_table_name}({columns_str}) VALUES ({binds_str})'

    def __init__(self, db, log_table_name):
        logging.Handler.__init__(self)
        self._log_table_name = log_table_name
        self._db = db
        self.conn = sqlite3.connect(self._db)
        self._create_tab_sql = self._get_create_tab_sql()
        self._insert_sql = self._get_insert_sql()
        # print(self._create_tab_sql)
        # print(self._insert_sql)
        self.conn.execute(self._create_tab_sql)
        self.conn.commit()

    def emit(self, record):
        ''' вставка записи в лог по событию '''
        try:
            params = self._fill_params(record)
            self.conn.execute(self._get_insert_sql(), params)
            self.conn.commit()
        except sqlite3.Error:
            self.conn.rollback()

    def get_logrecord_def(self):
        ''' дефолтные значения это None '''
        return {k:None for k in self._get_logrecord_attributes()}

    def _fill_params(self, record):
        ''' обработчик параметров лога - подготовка для вставки в таблицу,
        важно наличие всех полей, которые требуются для вставки '''
        params = {}
        for k, v in self.get_logrecord_def().items():
            if k in record.__dict__.keys():
                record_v = getattr(record, k)
                # print('*', k, type(record_v))
                if isinstance(record_v, (int, str, float)) or record_v is None:
                    params[k] = record_v
                else:
                    # страховка
                    params[k] = str(record_v)
                # частный случай, для создания читабельного времени
                if k == 'created' and isinstance(record_v, float):
                    params['asctime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record_v))
            else:
                # дефолтное значение
                params[k] = v
        return params
