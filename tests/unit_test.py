import os

import asyncio
import json
from unittest.mock import Mock
from datetime import datetime

import ebayaiohttp
import babalooo
from adapters.SQLAlchemyAdapter import SQLAlchemyAdapter
from adapters.models import EbayItem, AmazonItem


def test_ebayaiohttp():
    '''Tests ebayaiohttp.find_advanced()'''
    dictionary = {
        'keywords': 'magic the gathering',
        'categoryId': '38292'
    }
    result = asyncio.get_event_loop().run_until_complete(ebayaiohttp.find_advanced(dictionary))
    assert isinstance(result, dict)
    assert result.get('findItemsAdvancedResponse')


def test_open_files():
    '''
    Tests open_files() is returning a list containing all the products in the json files
    Uses two files: products.json and products1.json
    '''
    dicts = [json.loads(open('products.json').read()), json.loads(open('products1.json').read())]
    jsons = (open('products.json'), open('products1.json'))
    product_list = babalooo.open_files(jsons)
    for d in dicts:
        assert d in product_list


def test_amazon_make_items(mocker):
    '''Mocks amazon response to test amazon_make_items is returning a list of found items'''
    mock_bs = mocker.patch('babalooo.BeautifulSoup')
    mock_bs.return_value.find.return_value = True
    mock_bs.return_value.return_value = [Mock(), ]
    mock_bs.return_value.return_value[0].ListPrice = Mock()
    mock_bs.return_value.return_value[0].ListPrice.FormattedPrice.text = 'EUR 10,99'
    mock_bs.return_value.return_value[0].ASIN.text = 'asin'
    mock_bs.return_value.return_value[0].ItemAttributes.Title.text = 'title'
    mock_bs.return_value.return_value[0].DetailPageURL.text = 'url'
    mock_bs.return_value.return_value[0].ItemAttributes.Binding.text = 'category'
    response = babalooo.amazon_make_items(None, 1)  # amazon_make_items(response is not necessary, count)
    assert isinstance(response, list)
    assert response[0]['id'] == 'asin'
    assert response[0]['title'] == 'title'
    assert response[0]['url'] == 'url'
    assert response[0]['price_currency'] == 'EUR'
    assert response[0]['price_amount'] == 10.99
    assert response[0]['category'] == 'category'


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
        ('listingInfo', [dict(endTime=['2000-01-01T00:00:0012345'])]),
        # ebay date format is YYYY-MM-DDTHH:MM:SSxxxxx with xxxxx being 5 not relevant characters
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
    asyncio.get_event_loop().run_until_complete(babalooo.ebay_observer(conn, None, 1))
    #                                                         Not necessary --'
    assert conn.item_in_database('id', EbayItem)
    os.remove('test_db.sqlite3')


def test_amazon_observer(mocker):
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
    babalooo.amazon_observer(conn, dict(keywords=None), 1)
    assert conn.item_in_database('id', AmazonItem)
    os.remove('test_db.sqlite3')
