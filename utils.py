import os


def get_access_key():
    try:
        return os.environ['AWS_ACCESS_KEY_ID']
    except KeyError:
        raise KeyError('AWS_ACCESS_KEY_ID not set')


def get_secret_key():
    try:
        return os.environ['AWS_SECRET_ACCESS_KEY']
    except KeyError:
        raise KeyError('AWS_SECRET_ACCESS_KEY not set')


def get_associate_tag():
    try:
        return os.environ['AMAZON_ASSOCIATE_TAG']
    except KeyError:
        raise KeyError('AMAZON_ASSOCIATE_TAG not set')


def get_ebay_app_id():
    try:
        return os.environ['EBAY_APP_ID']
    except KeyError:
        raise KeyError('EBAY_APP_ID not set')
