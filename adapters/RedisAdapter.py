import redis

from .adapter import Adapter


class RedisAdapter(Adapter):

    def __init__(self, db, host='localhost'):
        self.conn = redis.StrictRedis(host=host, db=db, decode_responses=True)

    def item_in_database(self, itemId):
        return self.conn.hgetall(itemId) != {}

    def price_changed(self, item):
        old_price = float(self.conn.hget(item['itemId'][0], 'price_amount'))
        new_price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])
        return old_price != new_price

    def update(self, item):
        print('%s %s : price has changed. Now it\'s %s %s' % (
            item['itemId'][0],
            item['title'][0],
            item['sellingStatus'][0]['currentPrice'][0]['__value__'],
            item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        self.conn.hset(item['itemId'],
                       'price_amount',
                       item['sellingStatus'][0]['currentPrice'][0]['__value__'])

    def create(self, item):
        print('Found new item: %s %s. Price: %s %s' % (
            item['itemId'][0],
            item['title'][0],
            item['sellingStatus'][0]['currentPrice'][0]['__value__'],
            item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        self.conn.hmset(item['itemId'][0], {
                        'URL': item['viewItemURL'][0],
                        'price_amount': item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                        'price_currency': item['sellingStatus'][0]['currentPrice'][0]['@currencyId'],
                        'title': item['title'][0],
                        'expire': item['listingInfo'][0]['endTime'][0],
                        'product': '%s %s' % (
                            item['primaryCategory'][0]['categoryName'][0],
                            item['primaryCategory'][0]['categoryId'][0])})
