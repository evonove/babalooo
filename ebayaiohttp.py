import aiohttp

from utils import EBAY_APP_ID


async def find_advanced(dictionary):
    """
    Asynchronous findItemsAdvanced from ebay Finding API using aiohttp.
    RESPONSE-DATA-FORMAT is JSON
    """
    url = 'http://svcs.ebay.com/services/search/FindingService/v1'
    params = {
        'OPERATION-NAME': 'findItemsAdvanced',
        'SERVICE-VERSION': '1.0.0',
        'SECURITY-APPNAME': EBAY_APP_ID,
        'RESPONSE-DATA-FORMAT': 'JSON',
        'keywords': dictionary["keywords"].replace(' ', '%20'),
        'categoryId': dictionary['categoryId']
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json(content_type='text/plain')
