import os

import asyncio
import json
from datetime import datetime

import babalooo
from adapters.SQLAlchemyAdapter import SQLAlchemyAdapter
from adapters.models import EbayItem, AmazonItem


def test_open_files():
    '''
    Tests open_files() is returning a list containing all the products in the json files
    Uses two files: tests/products.json and tests/products1.json
    '''
    dicts = [json.loads(open('tests/products.json').read()), json.loads(open('tests/products1.json').read())]
    jsons = (open('tests/products.json'), open('tests/products1.json'))
    product_list = babalooo.open_files(jsons)
    for d in dicts:
        assert d in product_list


def test_amazon_make_items():
    '''Mocks amazon response to test amazon_make_items is returning a list of found items'''
    items = babalooo.amazon_make_items(open('tests/amazon.xml').read().encode(), 1)
    assert isinstance(items, list)
    assert items[0]['id'] == 'B071RM7CYZ'
    assert items[0]['title'] == "Magic The Gathering: Amonkhet Deckbuilder's Toolkit - Italiano"
    assert items[0]['url'] == 'https://www.amazon.it/Magic-Gathering-Amonkhet-Deckbuilders-Italiano/dp/B071RM7CYZ?' \
        'SubscriptionId=AKIAITD536YOTTXF3VUA&tag=vicaroni-21&linkCode=xm2&camp=2025&' \
        'creative=165953&creativeASIN=B071RM7CYZ'
    assert items[0]['price_currency'] == 'EUR'
    assert items[0]['price_amount'] == 24.88
    assert items[0]['category'] == 'Giocattolo'


def test_ebay_make_items(mocker):
    '''Mocks ebay response to test ebay_make_items is returning a list of found items'''
    mock = [dict(searchResult=None), ]
    mocker.patch.dict(mock[0])
    mock[0]['searchResult'] = [dict(item=None), ]
    mocker.patch.dict(mock[0]['searchResult'][0])
    mapping = [
        ('itemId', None),
        ('title', None),
        ('viewItemURL', None),
        ('sellingStatus', [dict(currentPrice=[
            dict([
                ('__value__', 10.99),
                ('@currencyId', 'EUR')])])]),
        # ebay date format is YYYY-MM-DDTHH:MM:SSxxxxx with xxxxx being 5 not relevant characters
        ('listingInfo', [dict(endTime=['2000-01-01T00:00:0012345'])]),
        ('primaryCategory', [dict([
            ('categoryName', ['category']),
            ('categoryId', ['categoryId'])])])
    ]  # mapping for ebay response
    mock[0]['searchResult'][0]['item'] = [dict(mapping), ]
    mock[0]['searchResult'][0]['item'][0]['itemId'] = ['id']
    mock[0]['searchResult'][0]['item'][0]['title'] = ['title']
    mock[0]['searchResult'][0]['item'][0]['viewItemURL'] = ['url']
    response = babalooo.ebay_make_items(mock, 1)
    assert isinstance(response, list)
    assert response[0]['id'] == 'id'
    assert response[0]['title'] == 'title'
    assert response[0]['url'] == 'url'
    assert response[0]['price_currency'] == 'EUR'
    assert response[0]['price_amount'] == 10.99
    assert response[0]['category'] == 'category categoryId'
    assert str(response[0]['expire']) == '2000-01-01 00:00:00'


def test_ebay_observer(mocker):
    '''Tests ebay_observer() is properly saving items in database'''
    conn = SQLAlchemyAdapter('sqlite', 'test_db.sqlite3')

    async def mock_find():
        return dict(findItemsAdvancedResponse=True)
    mocker.patch('babalooo.find_advanced', return_value=mock_find())
    mocker.patch('babalooo.ebay_make_items', return_value=[dict(
        id='id',
        title='title',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        expire=datetime(2000, 1, 1),
        category='category'
    )])
    # ebay_observer() is called passing product=None because it is only used in find_advanced() (mocked)
    asyncio.get_event_loop().run_until_complete(babalooo.ebay_observer(conn, None, 1))
    assert conn.item_in_database('id', EbayItem)
    os.remove('test_db.sqlite3')


def test_amazon_observer(mocker):
    '''Tests amazon_observer() is properly saving items in database'''
    conn = SQLAlchemyAdapter('sqlite', 'test_db.sqlite3')
    mock_amazon = mocker.patch('babalooo.bottlenose.Amazon')
    mock_amazon.ItemSearch.return_value = None
    mocker.patch('babalooo.amazon_make_items', return_value=[dict(
        id='id',
        title='title',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        category='category'
    )])
    mocker.patch('babalooo.get_associate_tag', return_value='associate tag')
    mocker.patch('babalooo.get_amazon_region', return_value='amazon region')
    babalooo.amazon_observer(conn, dict(keywords=None), 1)
    assert conn.item_in_database('id', AmazonItem)
    os.remove('test_db.sqlite3')
