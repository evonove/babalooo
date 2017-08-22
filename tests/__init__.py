import os

import pytest


def amazon_secret_key_exist():
    try:
        os.environ['AWS_SECRET_ACCESS_KEY']
    except KeyError:
        return False
    return True


def amazon_access_key_exist():
    try:
        os.environ['AWS_ACCESS_KEY_ID']
    except KeyError:
        return False
    return True


def amazon_associate_tag_exist():
    try:
        os.environ['AMAZON_ASSOCIATE_TAG']
    except KeyError:
        return False
    return True


def ebay_app_id_exists():
    try:
        os.environ['EBAY_APP_ID']
    except KeyError:
        return False
    return True


def redis_path_exists():
    try:
        os.environ['REDIS_SERVER_PATH']
    except KeyError:
        return False
    return True


missing_secret_key = pytest.mark.skipif(not amazon_secret_key_exist(), reason='Missing Amazon secret access key')
missing_access_key = pytest.mark.skipif(not amazon_access_key_exist(), reason='Missing Amazon access key')
missing_associate_tag = pytest.mark.skipif(not amazon_associate_tag_exist(), reason='Missing Amazon associate tag')
missing_ebay_app_id = pytest.mark.skipif(not ebay_app_id_exists(), reason='Missing Ebay AppID')
missing_redis_server = pytest.mark.skipif(not redis_path_exists(), reason='Missing redis-server')
REDIS_SERVER_PATH = os.getenv('REDIS_SERVER_PATH')
