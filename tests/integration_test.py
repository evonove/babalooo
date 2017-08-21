import bottlenose
import asyncio

import ebayaiohttp
import utils
from . import missing_ebay_app_id, missing_secret_key, missing_access_key, missing_associate_tag, missing_amazon_region


@missing_ebay_app_id
def test_ebayaiohttp():
    '''Tests ebayaiohttp.find_advanced() is returning findItemsAdvancedResponse decoded json'''
    dictionary = {
        'keywords': 'magic the gathering',
        'categoryId': '38292'
    }
    result = asyncio.get_event_loop().run_until_complete(ebayaiohttp.find_advanced(dictionary))
    assert isinstance(result, dict)
    assert result.get('findItemsAdvancedResponse')


@missing_secret_key
@missing_access_key
@missing_associate_tag
@missing_amazon_region
def test_bottlenose():
    '''
    Tests integration with bottlenose.
    bottlenose.Amazon.ItemSearch() should return an XML containing the response
    '''
    amazon = bottlenose.Amazon(AssociateTag=utils.get_associate_tag(), Region=utils.get_amazon_region())
    product = {"keywords": "magic"}
    response = amazon.ItemSearch(Keywords=product['keywords'], SearchIndex='All', ResponseGroup='Medium')
    assert str(response).find('<ItemSearchResponse') > 0
