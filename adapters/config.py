from . import RedisAdapter
from . import SQLAlchemyAdapter


def config(database):
    '''Configures the chosen database. Returns an adapter instance for calling Adapter.process()'''
    if database == 'sqlite':
        # argument tells SQLAlchemy to use SQLite database
        return SQLAlchemyAdapter.SQLAlchemyAdapter('sqlite')
    elif database == 'postgresql':
        # arguments are (DB_program, db_name, user, password, (optional, default = localhost) host)
        return SQLAlchemyAdapter.SQLAlchemyAdapter('postgresql', 'ebay', 'ebay', 'ebay')
    elif database == 'redis':
        return RedisAdapter.RedisAdapter(0)
