import os

import pytest


def amazon_secret_key_exist():
    try:
        os.environ['AWS_SECRET_ACCESS_KEY']
        return True
    except KeyError:
        return False


def amazon_access_key_exist():
    try:
        os.environ['AWS_ACCESS_KEY_ID']
        return True
    except KeyError:
        return False


def amazon_associate_tag_exist():
    try:
        os.environ['AMAZON_ASSOCIATE_TAG']
        return True
    except KeyError:
        return False


def amazon_region_exist():
    try:
        os.environ['AMAZON_REGION']
        return True
    except KeyError:
        return False


def ebay_app_id_exists():
    try:
        os.environ['EBAY_APP_ID']
        return True
    except KeyError:
        return False


missing_secret_key = pytest.mark.skipif(not amazon_secret_key_exist(), reason='Missing Amazon secret access key')
missing_access_key = pytest.mark.skipif(not amazon_access_key_exist(), reason='Missing Amazon access key')
missing_associate_tag = pytest.mark.skipif(not amazon_associate_tag_exist(), reason='Missing Amazon associate tag')
missing_amazon_region = pytest.mark.skipif(not amazon_region_exist(), reason='Missing Amazon region')
missing_ebay_app_id = pytest.mark.skipif(not ebay_app_id_exists(), reason='Missing Ebay AppID')
