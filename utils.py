import os


def get_associate_tag():
    try:
        return os.environ['AMAZON_ASSOCIATE_TAG']
    except KeyError:
        raise KeyError('AMAZON_ASSOCIATE_TAG not set')


def get_amazon_region():
    try:
        return os.environ['AMAZON_REGION']
    except KeyError:
        raise KeyError('AMAZON_REGION not set')


def get_ebay_app_id():
    try:
        return os.environ['EBAY_APP_ID']
    except KeyError:
        raise KeyError('EBAY_APP_ID not set')


AMAZON_ASSOCIATE_TAG = get_associate_tag()
AMAZON_REGION = get_amazon_region()
EBAY_APP_ID = get_ebay_app_id()
