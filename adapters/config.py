from . import RedisAdapter
from . import SQLAlchemyAdapter


def config(database):
    if database == 'sqlite':
        return SQLAlchemyAdapter.SQLAlchemyAdapter('sqlite')
    elif database == 'postgresql':
        return SQLAlchemyAdapter.SQLAlchemyAdapter('postgresql', 'ebay', 'ebay', 'ebay')
    elif database == 'redis':
        return RedisAdapter.RedisAdapter(0)
