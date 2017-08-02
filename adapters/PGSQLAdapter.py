import psycopg2

from .adapter import Adapter


class PGSQLAdapter(Adapter):

    cur = None

    def __init__(self, dbname, user, password, host='localhost'):
        try:
            self.conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (
                host,
                dbname,
                user,
                password
            ))
            self.cur = self.conn.cursor()
            self.cur.execute('create table if not exists items(\
                            itemId varchar primary key,\
                            url varchar,\
                            price_amount varchar,\
                            price_currency varchar,\
                            title varchar,\
                            expire varchar,\
                            product varchar);')
            self.conn.commit()
        except psycopg2.Error as err:
            print(err)

    def item_in_database(self, itemId):
        self.cur.execute("select * from items where itemId=%s;", (itemId,))
        return self.cur.fetchone() is not None

    def price_changed(self, item):
        self.cur.execute("select price_amount from items where itemId=%s;", (item['itemId'][0],))
        old_price = float(self.cur.fetchone()[0])
        new_price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])
        return old_price != new_price

    def create_or_update(self, item):
        try:
            if self.item_in_database(item['itemId'][0]):
                if self.price_changed(item):
                    print('%s %s : price has changed. Now it\'s %s %s' % (
                        item['itemId'][0],
                        item['title'][0],
                        item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                        item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
                    self.cur.execute("update items set price_amount = %s where itemId = %s;", (
                                    item['sellingStatus'][0]['currentPrice'][0]['__value__'], item['itemId'][0]))
            else:
                print('Found new item: %s %s. Price: %s %s' % (
                    item['itemId'][0],
                    item['title'][0],
                    item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                    item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
                self.cur.execute("insert into items values(%s, %s, %s, %s, %s, %s, %s);", (
                                item['itemId'][0],
                                item['viewItemURL'][0],
                                item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                                item['sellingStatus'][0]['currentPrice'][0]['@currencyId'],
                                item['title'][0],
                                item['listingInfo'][0]['endTime'][0],
                                "%s %s" % (
                                    item['primaryCategory'][0]['categoryName'][0],
                                    item['primaryCategory'][0]['categoryId'][0])))
        except psycopg2.Error as err:
            print(err)

    def commit(self):
        try:
            self.conn.commit()
        except psycopg2.Error as err:
            print(err)

    def close(self):
        try:
            self.cur.close()
            self.conn.close()
        except psycopg2.Error as err:
            print(err)
