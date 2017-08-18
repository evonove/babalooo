import os

from datetime import datetime

from adapters.SQLAlchemyAdapter import SQLAlchemyAdapter
from adapters.models import EbayItem, AmazonItem


def test_SQLAlchemy_item_in_database():
    '''Tests SQLAlchemyAdapter.item_in_database() properly returns True after creating an entry'''
    conn = SQLAlchemyAdapter('sqlite', 'test_db.sqlite3')
    conn.session.add(EbayItem(
        itemId='id',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        title='title',
        expire=datetime(2000, 1, 1),
        category='category'
    ))
    assert conn.item_in_database('id', EbayItem)
    conn.session.add(AmazonItem(
        itemId='id',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        title='title',
        category='category'
    ))
    assert conn.item_in_database('id', AmazonItem)
    os.remove('test_db.sqlite3')


def test_SQLAlchemy_price_changed():
    '''Tests SQLAlchemyAdapter.price_changed() propertly returns True passing a different price'''
    conn = SQLAlchemyAdapter('sqlite', 'test_db.sqlite3')
    conn.session.add(EbayItem(
        itemId='id',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        title='title',
        expire=datetime(2000, 1, 1),
        category='category'
    ))
    assert conn.price_changed(dict(id='id', price_amount=11.99), EbayItem)
    os.remove('test_db.sqlite3')


def test_SQLAlchemy_update():
    '''Tests item has been updated after calling SQLAlchemyAdapter.update() passing a different price'''
    conn = SQLAlchemyAdapter('sqlite', 'test_db.sqlite3')
    conn.session.add(EbayItem(
        itemId='id',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        title='title',
        expire=datetime(2000, 1, 1),
        category='category'
    ))
    conn.update(dict(
        id='id',
        title='title',
        price_amount=11.99,
        price_currency='EUR'
    ), EbayItem)
    assert conn.session.query(EbayItem.price_amount).filter(EbayItem.itemId == 'id').scalar() == 11.99
    os.remove('test_db.sqlite3')


def test_SQLAlchemy_create():
    '''Tests entry presence after calling SQLAlchemyAdapter.create()'''
    conn = SQLAlchemyAdapter('sqlite', 'test_db.sqlite3')
    item = dict(
        id='id',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        title='title',
        expire=datetime(2000, 1, 1),
        category='category'
    )
    conn.create(item, EbayItem)
    assert conn.item_in_database('id', EbayItem)
    item = dict(
        id='id',
        url='url',
        price_amount=10.99,
        price_currency='EUR',
        title='title',
        category='category'
    )
    conn.create(item, AmazonItem)
    assert conn.item_in_database('id', AmazonItem)
    os.remove('test_db.sqlite3')
