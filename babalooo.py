import asyncio
import time
import logging
import click
import json
import bottlenose
from bs4 import BeautifulSoup
from datetime import datetime

from ebayaiohttp import find_advanced
import adapters.config


def amazon_make_items(response, count):
    '''
    Constructs a list of dict objects containing information about items
    Amazon returns search results as XML to be parsed using BeautifulSoup
    '''
    soup = BeautifulSoup(response, 'xml')
    if soup.find('ItemSearchResponse') is not None:
        items = []
        for item in soup('Item')[:count]:
            if item.ListPrice is not None:
                price = item.ListPrice.FormattedPrice.text.split()
                items.append({
                    'id': item.ASIN.text,
                    'title': item.ItemAttributes.Title.text,
                    'url': item.DetailPageURL.text,
                    'price_currency': price[0],
                    'price_amount': float(price[1].replace(',', '.')),
                    'category': item.ItemAttributes.Binding.text})
            else:
                count += 1
        return items
    return None


def ebay_make_items(response, count):
    '''
    Constructs a list of dict objects containing information about items
    Ebay returns search results as JSON (already decoded in ebayaiohttp.find_advanced())
    '''
    items = [{
        'id': item['itemId'][0],
        'title': item['title'][0],
        'url': item['viewItemURL'][0],
        'price_amount': float(item['sellingStatus'][0]['currentPrice'][0]['__value__']),
        'price_currency': item['sellingStatus'][0]['currentPrice'][0]['@currencyId'],
        'expire': datetime.strptime(item['listingInfo'][0]['endTime'][0][:-5], '%Y-%m-%dT%H:%M:%S'),
        #                   `--converts the string endTime to Python's datetime using format YYYY-MM-DD HH:MM:SS
        'category': '%s %s' % (
          item['primaryCategory'][0]['categoryName'][0],
          item['primaryCategory'][0]['categoryId'][0])
    } for item in response[0]['searchResult'][0]['item'][:count]]
    return items


def open_files(lst):
    '''Opens a list of jsons and returns a list of products to search'''
    products_list = []
    for f in lst:
        elem = json.loads(f.read())
        if isinstance(elem, list):
            products_list += elem
        elif isinstance(elem, dict):
            products_list.append(elem)
    return products_list


async def ebay_observer(conn, product, count):
    '''Asynchronous search for product. Saves items found in database'''
    logging.info('ebay: searching for %s' % product)
    response = await find_advanced(product)
    response = response.get('findItemsAdvancedResponse')
    if response is not None:
        logging.info('ebay: found %s' % product)
        items = ebay_make_items(response, count)
        conn.process(items, 'ebay')
    else:
        fail = 'ebay: failed search for %s' % product
        logging.warning(fail)
        print(fail)


def amazon_observer(conn, product, count):
    '''Searches for product. Saves items found in database'''
    logging.info('amazon: searching for %s' % product)
    keys = open('keys').read().split('\n')
    amazon = bottlenose.Amazon(keys[0], keys[1], keys[2], Region=keys[3])
    response = amazon.ItemSearch(Keywords=product['keywords'], SearchIndex='All', ResponseGroup='Medium')
    items = amazon_make_items(response, count)
    if items is not None:
        logging.info('amazon: found %s' % product)
        conn.process(items, 'amazon')
    else:
        fail = 'amazon: failed search for %s' % product
        logging.warning(fail)
        print(fail)


@click.command()
@click.argument('search_details_json', type=click.File('rb'), nargs=-1, required=True)
@click.option('--interval', default=60, help='Interval (in seconds) between each run', show_default=True)
@click.option('--count', default=10, help='Number of items to check', show_default=True)
@click.option('--database', default='sqlite', help='Database to use', show_default=True,
              type=click.Choice(['sqlite', 'postgresql', 'redis']))
def main(count, interval, search_details_json, database):
    try:
        conn = adapters.config.config(database)
        products_list = open_files(search_details_json)
        loop = asyncio.get_event_loop()
        while(True):
            tasks = [asyncio.ensure_future(ebay_observer(conn, product, count)) for product in products_list]
            loop.run_until_complete(asyncio.wait(tasks))
            for product in products_list:
                amazon_observer(conn, product, count)
            time.sleep(interval)
            print('\n%s\n' % ('=' * 100))
    except KeyboardInterrupt:
        exit(0)
