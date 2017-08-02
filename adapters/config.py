from . import SQLiteAdapter
from . import PGSQLAdapter
from . import RedisAdapter


def config(database):
    if database == 'sqlite':
        return SQLiteAdapter.SQLiteAdapter()
    elif database == 'postgresql':
        return PGSQLAdapter.PGSQLAdapter('ebay', 'ebay', 'ebay')
    elif database == 'redis':
        return RedisAdapter.RedisAdapter(0)
