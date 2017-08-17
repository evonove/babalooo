from .models import EbayItem, AmazonItem


class Adapter:

    def item_in_database(self, itemId):
        '''Returns True if item with id = itemId is in database'''
        raise NotImplementedError

    def price_changed(self, item):
        '''Returns True if price has changed since the last check'''
        raise NotImplementedError

    def create(self, item):
        '''Creates an entry for item'''
        raise NotImplementedError

    def update(self, item):
        '''Updates item's price'''
        raise NotImplementedError

    def process(self, items, table):
        '''
        If item doesn't exist in database, its entry is created.
        If item's price has changed, its entry is updated.
        '''
        if table == 'ebay':
            table_class = EbayItem
        elif table == 'amazon':
            table_class = AmazonItem
        for item in items:
            if not self.item_in_database(item['id'], table_class):
                self.create(item, table_class)
            elif self.price_changed(item, table_class):
                self.update(item, table_class)
