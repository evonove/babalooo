from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Float


class Base:
    '''Class describing the model for items table in database'''
    itemId = Column(String, primary_key=True)
    url = Column(String)
    price_amount = Column(Float)
    price_currency = Column(String)
    title = Column(String)
    category = Column(String)


Base = declarative_base(cls=Base)


class EbayItem(Base):
    __tablename__ = 'ebay'
    expire = Column(DateTime)


class AmazonItem(Base):
    __tablename__ = 'amazon'
