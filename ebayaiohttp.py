import aiohttp

async def find_advanced(dictionary):
    """Asynchronous findItemsAdvanced from ebay Finding API using aiohttp"""
    url = 'http://svcs.ebay.com/services/search/FindingService/v1'
    params = {
        'OPERATION-NAME': 'findItemsAdvanced',
        'SERVICE-VERSION': '1.0.0',
        'SECURITY-APPNAME': 'Riccardo-ebay-PRD-4c6cc25dc-e28c4d3d',
        'RESPONSE-DATA-FORMAT': 'JSON',
        'keywords': dictionary["keywords"].replace(' ', '%20'),
        'categoryId': dictionary['categoryId']
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json(content_type='text/plain')
