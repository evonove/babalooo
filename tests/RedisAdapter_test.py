from datetime import datetime
from pytest_redis import factories

from adapters.RedisAdapter import RedisAdapter
from . import missing_redis_server, REDIS_SERVER_PATH


redis_my_proc = factories.redis_proc(port=6379, db_count=1, executable=REDIS_SERVER_PATH)
redis_fix = factories.redisdb('redis_my_proc', decode=True)


@missing_redis_server
def test_redis_item_in_database(redis_fix):
    '''Tests RedisAdapter.item_in_database() properly returns True after creating an entry'''
    redis_fix.hmset('id', {
                    'URL': 'url',
                    'price_amount': 10.99,
                    'price_currency': 'price_currency',
                    'title': 'title',
                    'expire': 'expire',
                    'category': 'category'})
    assert RedisAdapter().item_in_database('id')


@missing_redis_server
def test_redis_price_changed(redis_fix):
    '''Tests RedisAdapter.price_changed() propertly returns True passing a different price'''
    redis_fix.hmset('id', {
                    'URL': 'url',
                    'price_amount': 10.99,
                    'price_currency': 'price_currency',
                    'title': 'title',
                    'expire': 'expire',
                    'category': 'category'})
    assert RedisAdapter().price_changed(dict(id='id', price_amount=11.99))


@missing_redis_server
def test_redis_update(redis_fix):
    '''Tests item has been updated after calling RedisAdapter.update() passing a different price'''
    redis_fix.hmset('id', {
                    'URL': 'url',
                    'price_amount': 10.99,
                    'price_currency': 'price_currency',
                    'title': 'title',
                    'expire': 'expire',
                    'category': 'category'})
    RedisAdapter().update(dict(
        id='id',
        title='title',
        price_amount=11.99,
        price_currency='EUR'
    ))
    assert float(redis_fix.hget('id', 'price_amount')) == 11.99


@missing_redis_server
def test_redis_create(redis_fix):
    '''Tests entry presence after calling RedisAdapter.create()'''
    redis = RedisAdapter()
    item = dict(
        id='id',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        title='title',
        expire=datetime(2000, 1, 1),
        category='category'
    )
    redis.create(item)
    assert redis.item_in_database('id')
