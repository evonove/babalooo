from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from .adapter import Adapter
from .models import EbayItem, AmazonItem, Base


class SQLAlchemyAdapter(Adapter):

    def __init__(self, backend, database, user=None, password=None, host='localhost'):
        # creates engine for the chosen backend
        if backend == 'sqlite':
            engine = create_engine('sqlite:///%s' % database)
        elif backend == 'postgresql':
            engine = create_engine('postgresql+psycopg2://%s:%s@/%s?host=%s' % (user, password, database, host))
        Base.metadata.create_all(engine)  # creates the tables
        Session = sessionmaker(bind=engine)
        self.session = Session()  # session to be used for queries

    def item_in_database(self, itemId, table):
        return self.session.query(table.itemId).filter(table.itemId == itemId).one_or_none() is not None

    def price_changed(self, item, table):
        old_price = self.session.query(table.price_amount).filter(table.itemId == item['id']).scalar()
        return old_price != float(item['price_amount'])

    def update(self, item, table):
        price = float(item['price_amount'])
        print('%s %s : price has changed. Now it\'s %f %s' % (
            item['id'], item['title'], price, item['price_currency']))
        db_item = self.session.query(table).filter(table.itemId == item['id']).one()
        db_item.price_amount = price

    def create(self, item, table):
        print('Found new item: %s %s. Price: %s %s' % (
            item['id'],
            item['title'],
            item['price_amount'],
            item['price_currency']))
        if table == EbayItem:
            self.session.add(EbayItem(
                itemId=item['id'],
                url=item['url'],
                price_amount=item['price_amount'],
                price_currency=item['price_currency'],
                title=item['title'],
                expire=item['expire'],
                category=item['category']))
        elif table == AmazonItem:
            self.session.add(AmazonItem(
                itemId=item['id'],
                url=item['url'],
                price_amount=item['price_amount'],
                price_currency=item['price_currency'],
                title=item['title'],
                category=item['category']))

    def process(self, items, table):
        try:
            super().process(items, table)
            self.session.commit()
        except SQLAlchemyError:
            print('Failed saving in database')
            self.session.rollback()
