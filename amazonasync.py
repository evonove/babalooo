import aiohttp
from datetime import datetime
import hmac
from base64 import encodebytes

from utils import get_access_key, get_secret_key, get_associate_tag


async def item_search(dictionary):
    '''
    Asynchronous ItemSearch from Amazon Product Advertising API using aiohttp
    Returns response as XML
    '''
    url = 'webservices.amazon.it'
    path = '/onca/xml'
    now = datetime.now()
    params = dict(
        AWSAccessKeyId=get_access_key(),
        AssociateTag=get_associate_tag(),
        Keywords=dictionary['keywords'].replace(' ', '%20'),
        Operation='ItemSearch',
        ResponseGroup='Medium',
        SearchIndex='All',
        Service='AWSECommerceService',
        # timestamp with colon encoded as %3A
        Timestamp='%d-%02d-%02dT%02d%%3A%02d%%3A%02dZ' % (
            now.year, now.month, now.day, now.hour, now.minute, now.second))
    param_keys = list(params.keys())
    canonical_string = 'GET\n%s\n%s\n%s=%s&%s=%s&%s=%s&%s=%s&%s=%s&%s=%s&%s=%s&%s=%s' % (
        url, path, param_keys[0], params[param_keys[0]],
        param_keys[1], params[param_keys[1]],
        param_keys[2], params[param_keys[2]],
        param_keys[3], params[param_keys[3]],
        param_keys[4], params[param_keys[4]],
        param_keys[5], params[param_keys[5]],
        param_keys[6], params[param_keys[6]],
        param_keys[7], params[param_keys[7]])
    # HMAC-SHA256 signature made from message and secret access key
    params['Signature'] = encodebytes(hmac.new(
        get_secret_key().encode(),
        msg=canonical_string.encode(),
        digestmod='sha256').digest()).decode().replace('+', '%2B').replace('=', '%3D').replace('\n', '')
    async with aiohttp.ClientSession() as session:
        async with session.get('http://%s%s' % (url, path), params=params) as resp:
            return await resp.text()
