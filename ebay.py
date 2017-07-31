import sys

import json
import asyncio
import sqlite3
import time
import logging

from ebayaiohttp import find_advanced


def item_in_database(itemId):
    '''Returns True if item with id = itemId is in database'''
    return sql_conn.execute('select * from items where itemId="%s"' % itemId).fetchone() is not None


def price_changed(item):
    '''Returns True if price has changed since the last check'''
    old_price = float(sql_conn.execute('select price_amount from items where itemId="%s"' %
                                       item['itemId']).fetchone()[0])
    new_price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])
    return old_price != new_price


def insert(item):
    '''Insert into items table a new entry for item'''
    sql_conn.execute('insert into items values("%s", "%s", "%s", "%s", "%s", "%s", "%s %s")' % (
                    item['itemId'][0],
                    item['viewItemURL'][0],
                    item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                    item['sellingStatus'][0]['currentPrice'][0]['@currencyId'],
                    item['title'][0],
                    item['listingInfo'][0]['endTime'][0],
                    item['primaryCategory'][0]['categoryName'][0],
                    item['primaryCategory'][0]['categoryId'][0]))


def update_price(item):
    '''Updates current item's price in database'''
    sql_conn.execute('update items set price_amount = "%s" where itemId = "%s"' % (
                    item['sellingStatus'][0]['currentPrice'][0]['__value__'], item['itemId'][0]))


async def observer(product):
    '''Asynchronous search for product. Saves items found in database'''
    logging.info('searching for %s' % product)
    response = await find_advanced(product)
    logging.info('found %s' % product)
    for item in response['findItemsAdvancedResponse'][0]['searchResult'][0]['item'][:10]:
        if not item_in_database(item['itemId']):
            insert(item)
            print('Found new item: %s %s. Price: %s %s' % (
                item['itemId'][0],
                item['title'][0],
                item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        else:
            if price_changed(item):
                print('%s %s : price has changed. Now it\'s %s %s' % (
                    item['itemId'][0],
                    item['title'][0],
                    item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                    item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
                update_price(item)
    sql_conn.commit()

if __name__ == '__main__':
    '''Arguments are:
        - interval to wait between checks (in minutes),
        - name of the json file containing search details'''
    try:
        if len(sys.argv) != 3:
            print('Usage: python %s <interval_in_minutes> <search_details_json>' % sys.argv[0])
            exit(0)
        products_list = json.loads(open(sys.argv[2]).read())
        sql_conn = sqlite3.connect('products.sqlite3')
        sql_conn.execute('create table if not exists items(\
                        itemId text primary key,\
                        url text,\
                        price_amount text,\
                        price_currency text,\
                        title text,\
                        expire text,\
                        product text)')
        loop = asyncio.get_event_loop()
        while(True):
            tasks = [asyncio.ensure_future(observer(product)) for product in products_list]
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(int(sys.argv[1])*60)
            print('\n%s\n' % ('=' * 100))
    except KeyboardInterrupt:
        exit(0)
