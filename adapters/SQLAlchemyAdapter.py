from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from .adapter import Adapter


Base = declarative_base()


class Item(Base):
    '''Class describing the model for items table in database'''
    __tablename__ = 'items'
    itemId = Column(String, primary_key=True)
    url = Column(String)
    price_amount = Column(Float)
    price_currency = Column(String)
    title = Column(String)
    expire = Column(DateTime)
    category = Column(String)


class SQLAlchemyAdapter(Adapter):

    def __init__(self, backend, database=None, user=None, password=None, host='localhost'):
        # creates engine for the chosen backend
        if backend == 'sqlite':
            engine = create_engine('sqlite:///products.sqlite3')
        elif backend == 'postgresql':
            engine = create_engine('postgresql+psycopg2://%s:%s@/%s?host=%s' % (user, password, database, host))
        Base.metadata.create_all(engine) # creates the table
        Session = sessionmaker(bind=engine)
        self.session = Session() # session to be used for queries

    def item_in_database(self, itemId):
        return self.session.query(Item.itemId).filter(Item.itemId == itemId).one_or_none() is not None

    def price_changed(self, item):
        old_price = self.session.query(Item.price_amount).filter(Item.itemId == item['itemId'][0]).scalar()
        return old_price != float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])

    def update(self, item):
        price = float(item['sellingStatus'][0]['currentPrice'][0]['__value__'])
        print('%s %s : price has changed. Now it\'s %f %s' % (
            item['itemId'][0], item['title'][0], price,
            item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        db_item = self.session.query(Item).filter(Item.itemId == item['itemId'][0]).one()
        db_item.price_amount = price

    def create(self, item):
        print('Found new item: %s %s. Price: %s %s' % (
            item['itemId'][0],
            item['title'][0],
            item['sellingStatus'][0]['currentPrice'][0]['__value__'],
            item['sellingStatus'][0]['currentPrice'][0]['@currencyId']))
        self.session.add(Item(itemId=int(item['itemId'][0]),
                              url=item['viewItemURL'][0],
                              price_amount=item['sellingStatus'][0]['currentPrice'][0]['__value__'],
                              price_currency=item['sellingStatus'][0]['currentPrice'][0]['@currencyId'],
                              title=item['title'][0],
                              expire=datetime.strptime(item['listingInfo'][0]['endTime'][0][:-5], '%Y-%m-%dT%H:%M:%S'),
                                #  `--converts the string endTime to Python's datetime using format YYYY-MM-DD HH:MM:SS
                              category='%s %s' % (
                                item['primaryCategory'][0]['categoryName'][0],
                                item['primaryCategory'][0]['categoryId'][0])))

    def process(self, items):
        try:
            super().process(items)
            self.session.commit()
        except SQLAlchemyError:
            print('Failed saving in database')
            self.session.rollback()
