''' Handler SQLite для logging '''

from .sqlite_logging import SQLiteHandler

class SQLiteSensorHandler(SQLiteHandler):
    """ Handler SQLite для logging
    только добавлен  sensor_val для логгирования значения """

    LOG_VAL_FIELD = 'sensor_val'

    EXTRA_FIELDS = {
            LOG_VAL_FIELD: 'numeric'
        }

    @classmethod
    def _get_logrecord_attributes(cls):
        attributes = super()._get_logrecord_attributes()
        for k, v in SQLiteSensorHandler.EXTRA_FIELDS.items():
            attributes[k] = v
        return attributes
