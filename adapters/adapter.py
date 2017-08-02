import abc


class Adapter(abc.ABC):

    conn = None

    @abc.abstractmethod
    def item_in_database(self, itemId):
        '''Returns True if item with id = itemId is in database'''
        pass

    @abc.abstractmethod
    def price_changed(self, item):
        '''Returns True if price has changed since the last check'''
        pass

    @abc.abstractmethod
    def create_or_update(self, item):
        '''
        Checks if the item is in the database.
        If it is, updates its price, otherwise creates the entry for the item.
        '''
        pass

    @abc.abstractmethod
    def commit(self):
        '''Saves changes in the database'''
        pass

    @abc.abstractmethod
    def close(self):
        '''Closes the connection'''
        pass
