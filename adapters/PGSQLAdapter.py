import psycopg2

from .adapter import Adapter


class PGSQLAdapter(Adapter):

    def __init__(self, dbname, user, password, host='localhost'):
        self.conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (
            host,
            dbname,
            user,
            password
        ))
        with self.conn.cursor() as cursor:
            cursor.execute('create table if not exists items(\
                        itemId varchar primary key,\
                        url varchar,\
                        price_amount varchar,\
                        price_currency varchar,\
                        title varchar,\
                        expire varchar,\
                        product varchar);')
        self.conn.commit()

    def item_in_database(self, itemId):
        self.cursor.execute("select * from items where itemId=%s;", (itemId,))
        return self.cursor.fetchone() is not None

    def price_changed(self, item):
        self.cursor.execute("select price_amount from items where itemId=%s;", (item['itemId'][0],))
        old_price = float(self.cursor.fetchone()[0])
        new_price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])
        return old_price != new_price

    def update(self, item):
        print('%s %s : price has changed. Now it\'s %s %s' % (
            item['itemId'][0],
            item['title'][0],
            item['sellingStatus'][0]['currentPrice'][0]['__value__'],
            item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        self.cursor.execute("update items set price_amount = %s where itemId = %s;", (
                        item['sellingStatus'][0]['currentPrice'][0]['__value__'], item['itemId'][0]))

    def create(self, item):
        print('Found new item: %s %s. Price: %s %s' % (
            item['itemId'][0],
            item['title'][0],
            item['sellingStatus'][0]['currentPrice'][0]['__value__'],
            item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        self.cursor.execute("insert into items values(%s, %s, %s, %s, %s, %s, %s);", (
                        item['itemId'][0],
                        item['viewItemURL'][0],
                        item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                        item['sellingStatus'][0]['currentPrice'][0]['@currencyId'],
                        item['title'][0],
                        item['listingInfo'][0]['endTime'][0],
                        "%s %s" % (
                            item['primaryCategory'][0]['categoryName'][0],
                            item['primaryCategory'][0]['categoryId'][0])))

    def process(self, items):
        self.cursor = self.conn.cursor()
        try:
            super().process(items)
            self.conn.commit()
        except psycopg2.Error:
            print('Failed saving in database')
            self.conn.rollback()
        self.cursor.close()
