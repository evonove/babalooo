import asyncio
from datetime import datetime

import babalooo
from adapters.SQLAlchemyAdapter import SQLAlchemyAdapter
from adapters.models import EbayItem, AmazonItem


def test_open_files():
    '''
    Tests open_files() is returning a list containing all the products in the json files
    Uses two files: tests/products.json and tests/products1.json
    '''
    jsons = (open('tests/products.json'), open('tests/products1.json'))
    product_list = babalooo.open_files(jsons)
    assert product_list[0] == {
      "keywords": "magic",
      "categoryId": "38292"
    }
    assert product_list[1] == {
      "keywords": "magic",
      "categoryId": "11111"
    }


def test_amazon_make_items():
    '''Tests amazon_make_items is returning a list of found items'''
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
    '''Tests ebay_make_items is returning a list of found items'''
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
    conn = SQLAlchemyAdapter('sqlite', ':memory:')

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


def test_amazon_observer(mocker):
    '''Tests amazon_observer() is properly saving items in database'''
    conn = SQLAlchemyAdapter('sqlite', ':memory:')

    async def mock_find():
        return open('tests/amazon.xml').read().encode()
    mocker.patch('babalooo.item_search', return_value=mock_find())
    # amazon_observer() is called passing product=None because it is only used in item_search() (mocked)
    asyncio.get_event_loop().run_until_complete(babalooo.amazon_observer(conn, None, 1))
    assert conn.item_in_database('B071RM7CYZ', AmazonItem)
