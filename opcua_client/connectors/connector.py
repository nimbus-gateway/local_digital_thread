from abc import ABC, abstractmethod
class Connector:
    def __init__(self, dbname, host, username, password):
        self.connection = None
        self.dbname = dbname

    @abstractmethod
    def get_data(self, fields=[]):
        pass
    
    @abstractmethod
    def post_data(self, fields=[]):
        pass

    @abstractmethod
    def describe_table(self, table_name):
        pass

    @abstractmethod
    def disconnect(self):
        pass