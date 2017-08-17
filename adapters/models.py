from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Float


Base = declarative_base()


class EbayItem(Base):
    '''Class describing the model for items table in database'''
    __tablename__ = 'ebay'
    itemId = Column(String, primary_key=True)
    url = Column(String)
    price_amount = Column(Float)
    price_currency = Column(String)
    title = Column(String)
    expire = Column(DateTime)
    category = Column(String)


class AmazonItem(Base):
    '''Class describing the model for items table in database'''
    __tablename__ = 'amazon'
    itemId = Column(String, primary_key=True)
    url = Column(String)
    price_amount = Column(Float)
    price_currency = Column(String)
    title = Column(String)
    category = Column(String)
