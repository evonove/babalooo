import json
import asyncio
import time
import logging
import click

from ebayaiohttp import find_advanced
import adapters.config


async def observer(conn, product, count):
    '''Asynchronous search for product. Saves items found in database'''
    logging.info('searching for %s' % product)
    response = await find_advanced(product)
    response = response.get('findItemsAdvancedResponse')
    if response is not None:
        logging.info('found %s' % product)
        items = [item for item in response[0]['searchResult'][0]['item'][:count]]
        conn.process(items)
    else:
        fail = 'Failed search for %s' % product
        logging.warning(fail)
        print(fail)


@click.command()
@click.argument('interval')
@click.argument('search_details_json')
@click.option('--count', default=10, help='Number of items to check')
@click.option('--database',
              default='sqlite',
              help='Database to use',
              type=click.Choice(['sqlite', 'postgresql', 'redis']))
def main(count, interval, search_details_json, database):
    try:
        conn = adapters.config.config(database)
        products_list = json.loads(open(search_details_json).read())
        loop = asyncio.get_event_loop()
        while(True):
            tasks = [asyncio.ensure_future(observer(conn, product, count)) for product in products_list]
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(int(interval) * 60)
            print('\n%s\n' % ('=' * 100))
    except KeyboardInterrupt:
        exit(0)
