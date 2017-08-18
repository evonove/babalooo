from datetime import datetime

from adapters.RedisAdapter import RedisAdapter


def test_redis_item_in_database():
    '''Tests RedisAdapter.item_in_database() properly returns True after creating an entry'''
    redis = RedisAdapter(9)  # database 0 is default database
    redis.conn.hmset('id', {
                    'URL': 'url',
                    'price_amount': 10.99,
                    'price_currency': 'price_currency',
                    'title': 'title',
                    'expire': 'expire',
                    'category': 'category'})
    assert redis.item_in_database('id', None)  # None <= Redis hasn't got tables
    redis.conn.flushdb()


def test_redis_price_changed():
    '''Tests RedisAdapter.price_changed() propertly returns True passing a different price'''
    redis = RedisAdapter(9)  # database 0 is default database
    redis.conn.hmset('id', {
                    'URL': 'url',
                    'price_amount': 10.99,
                    'price_currency': 'price_currency',
                    'title': 'title',
                    'expire': 'expire',
                    'category': 'category'})
    assert redis.price_changed(dict(id='id', price_amount=11.99), None)
    redis.conn.flushdb()


def test_redis_update():
    '''Tests item has been updated after calling RedisAdapter.update() passing a different price'''
    redis = RedisAdapter(9)  # database 0 is default database
    redis.conn.hmset('id', {
                    'URL': 'url',
                    'price_amount': 10.99,
                    'price_currency': 'price_currency',
                    'title': 'title',
                    'expire': 'expire',
                    'category': 'category'})
    redis.update(dict(
        id='id',
        title='title',
        price_amount=11.99,
        price_currency='EUR'
    ), None)
    assert float(redis.conn.hget('id', 'price_amount')) == 11.99
    redis.conn.flushdb()


def test_redis_create():
    '''Tests entry presence after calling RedisAdapter.create()'''
    redis = RedisAdapter(9)  # database 0 is default database
    item = dict(
        id='id',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        title='title',
        expire=datetime(2000, 1, 1),
        category='category'
    )
    redis.create(item, None)
    assert redis.item_in_database('id', None)
    redis.conn.flushdb()
