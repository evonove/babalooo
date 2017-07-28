import sys

import json
import asyncio
import sqlite3
import time

from ebayaiohttp import find_advanced

async def observer(product):
    print('searching for %s' % product)
    response = await find_advanced(product)
    print('found %s' % product)
    for item in response['findItemsAdvancedResponse'][0]['searchResult'][0]['item'][:10]:
        if sql_conn.execute('select * from items where itemId="%s"' % item['itemId'][0]).fetchone() == None:
            sql_conn.execute('insert into items values("%s", "%s", "%s", "%s", "%s", "%s", "%s %s")'
                % (item['itemId'][0],
                item['viewItemURL'][0],
                item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                item['sellingStatus'][0]['currentPrice'][0]['@currencyId'],
                item['title'][0],
                item['listingInfo'][0]['endTime'][0],
                item['primaryCategory'][0]['categoryName'][0],
                item['primaryCategory'][0]['categoryId'][0]))
            print('Found new item: %s %s. Price: %s %s' % (
                item['itemId'][0],
                item['title'][0],
                item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        else:
            if float(sql_conn.execute('select price_amount from items where itemId="%s"' %
                item['itemId'][0]).fetchone()[0]) != float(item['sellingStatus'][0]['currentPrice'][0]['__value__']):
                print('%s %s : price has changed. Now it\'s %s %s' % (
                    item['itemId'][0],
                    item['title'][0],
                    item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                    item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
                sql_conn.execute('update items set price_amount = "%s" where itemId = "%s"' %
                    (item['sellingStatus'][0]['currentPrice'][0]['__value__'], item['itemId'][0]))
if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            print('Usage: python %s <interval_in_minutes> <search_details_json>' % sys.argv[0])
            exit(0)
        products_list = json.loads(open(sys.argv[2]).read())
        sql_conn = sqlite3.connect('products.sqlite3')
        loop = asyncio.get_event_loop()
        while(True):
            tasks = [asyncio.ensure_future(observer(product)) for product in products_list]
            loop.run_until_complete(asyncio.wait(tasks))
            sql_conn.commit()
            time.sleep(int(sys.argv[1])*60)
            print('\n============================================================================================\n')
    except KeyboardInterrupt:
        exit(0)
