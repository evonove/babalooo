import redis

from .adapter import Adapter


class RedisAdapter(Adapter):

    def __init__(self, db=0, host='localhost'):
        self.conn = redis.StrictRedis(host=host, db=db, decode_responses=True)

    def item_in_database(self, itemId, table=None):
        return self.conn.hgetall(itemId) != {}

    def price_changed(self, item, table=None):
        old_price = float(self.conn.hget(item['id'], 'price_amount'))
        return old_price != float(item['price_amount'])

    def update(self, item, table=None):
        print('%s %s : price has changed. Now it\'s %s %s' % (
            item['id'],
            item['title'],
            item['price_amount'],
            item['price_currency']))
        self.conn.hset(item['id'], 'price_amount', item['price_amount'])

    def create(self, item, table=None):
        print('Found new item: %s %s. Price: %s %s' % (
            item['id'],
            item['title'],
            item['price_amount'],
            item['price_currency']))
        self.conn.hmset(item['id'], {
                        'URL': item['url'],
                        'price_amount': item['price_amount'],
                        'price_currency': item['price_currency'],
                        'title': item['title'],
                        'expire': item['expire'],
                        'category': item['category']})
