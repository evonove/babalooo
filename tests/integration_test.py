import asyncio

from ebayaiohttp import find_advanced
from amazonasync import item_search
from . import missing_ebay_app_id, missing_secret_key, missing_access_key, missing_associate_tag


@missing_ebay_app_id
def test_ebayaiohttp():
    '''Tests ebayaiohttp.find_advanced() is returning findItemsAdvancedResponse decoded json'''
    dictionary = {
        'keywords': 'magic the gathering',
        'categoryId': '38292'
    }
    result = asyncio.get_event_loop().run_until_complete(find_advanced(dictionary))
    assert isinstance(result, dict)
    assert result.get('findItemsAdvancedResponse')


@missing_secret_key
@missing_access_key
@missing_associate_tag
def test_amazonasync():
    '''Tests amazonasync.item_search() is returning an XML containing the ItemSearchResponse tag'''
    product = {"keywords": "magic"}
    response = asyncio.get_event_loop().run_until_complete(item_search(product))
    assert response.find('<ItemSearchResponse') > 0
