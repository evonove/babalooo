import sqlite3

from .adapter import Adapter


class SQLiteAdapter(Adapter):

    def __init__(self):
        self.conn = sqlite3.connect('products.sqlite3')
        self.conn.execute('create table if not exists items(\
                        itemId text primary key,\
                        url text,\
                        price_amount text,\
                        price_currency text,\
                        title text,\
                        expire text,\
                        product text)')

    def item_in_database(self, itemId):
        return self.conn.execute('select * from items where itemId="%s"' % itemId).fetchone() is not None

    def price_changed(self, item):
        old_price = float(self.conn.execute('select price_amount from items where itemId="%s"' %
                                            item['itemId'][0]).fetchone()[0])
        new_price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])
        return old_price != new_price

    def update(self, item):
        print('%s %s : price has changed. Now it\'s %s %s' % (
            item['itemId'][0],
            item['title'][0],
            item['sellingStatus'][0]['currentPrice'][0]['__value__'],
            item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        self.conn.execute('update items set price_amount = "%s" where itemId = "%s"' % (
                        item['sellingStatus'][0]['currentPrice'][0]['__value__'], item['itemId'][0]))

    def create(self, item):
        print('Found new item: %s %s. Price: %s %s' % (
            item['itemId'][0],
            item['title'][0],
            item['sellingStatus'][0]['currentPrice'][0]['__value__'],
            item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        self.conn.execute('insert into items values("%s", "%s", "%s", "%s", "%s", "%s", "%s %s")' % (
                        item['itemId'][0],
                        item['viewItemURL'][0],
                        item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                        item['sellingStatus'][0]['currentPrice'][0]['@currencyId'],
                        item['title'][0],
                        item['listingInfo'][0]['endTime'][0],
                        item['primaryCategory'][0]['categoryName'][0],
                        item['primaryCategory'][0]['categoryId'][0]))

    def process(self, items):
        try:
            super().process(items)
            self.conn.commit()
        except sqlite3.Error:
            print('Failed saving in database')
            self.conn.rollback()
