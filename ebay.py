import json
import asyncio
import sqlite3
import time
import logging
import click

from ebayaiohttp import find_advanced


def item_in_database(sql_conn, itemId):
    '''Returns True if item with id = itemId is in database'''
    return sql_conn.execute('select * from items where itemId="%s"' % itemId).fetchone() is not None


def price_changed(sql_conn, item):
    '''Returns True if price has changed since the last check'''
    old_price = float(sql_conn.execute('select price_amount from items where itemId="%s"' %
                                       item['itemId'][0]).fetchone()[0])
    new_price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])
    return old_price != new_price


def insert(sql_conn, item):
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


def update_price(sql_conn, item):
    '''Updates current item's price in database'''
    sql_conn.execute('update items set price_amount = "%s" where itemId = "%s"' % (
                    item['sellingStatus'][0]['currentPrice'][0]['__value__'], item['itemId'][0]))


async def observer(sql_conn, product, count):
    '''Asynchronous search for product. Saves items found in database'''
    logging.info('searching for %s' % product)
    response = await find_advanced(product)
    logging.info('found %s' % product)
    for item in response['findItemsAdvancedResponse'][0]['searchResult'][0]['item'][:count]:
        if not item_in_database(sql_conn, item['itemId'][0]):
            insert(sql_conn, item)
            print('Found new item: %s %s. Price: %s %s' % (
                item['itemId'][0],
                item['title'][0],
                item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        else:
            if price_changed(sql_conn, item):
                print('%s %s : price has changed. Now it\'s %s %s' % (
                    item['itemId'][0],
                    item['title'][0],
                    item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                    item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
                update_price(sql_conn, item)
    sql_conn.commit()

@click.command()
@click.argument('interval')
@click.argument('search_details_json')
@click.option('--count', default=10, help='Number of items to check')
def main(count, interval, search_details_json):
    try:
        products_list = json.loads(open(search_details_json).read())
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
            tasks = [asyncio.ensure_future(observer(sql_conn, product, count)) for product in products_list]
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(int(interval) * 60)
            print('\n%s\n' % ('=' * 100))
    except KeyboardInterrupt:
        exit(0)
