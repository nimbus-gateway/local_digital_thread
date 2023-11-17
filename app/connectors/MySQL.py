import json
import mysql
from mysql import connector
from flask import jsonify
import logging
from datetime import datetime

import sys
sys.path.append("..")

_logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod
class Connector:
    def __init__(self,):
        self.connection = None
        # self.dbname = dbname

    @abstractmethod
    def connect_(self, dbname, host, username, password):
        pass

    @abstractmethod
    def get_data(self, mapping={}):
        pass

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

class MySQL(Connector):
    def __init__(self):
        self.connection = None

    def connect_(self, dbname, host, username, password):
        try:
            self.connection = mysql.connector.connect(
                        host=host,
                        user=username,
                        password=password,
                        database= dbname,
                        auth_plugin='mysql_native_password'
                    )
            return True
        except Exception as e:
            _logger.error("Error Occured")
            print(e)
            return False
        
    def connect(self, transformation={}, connection_profile={}):

        _logger.info("Arguments Recieved ")
        return self.connect_(transformation['dbname'], connection_profile['host'], connection_profile['username'], connection_profile['password'])

    def disconnect(self):
        self.connection.disconnect()

    def get_latest_data(self, table, col_names=[]):
        cursor = self.connection.cursor(buffered=True)

        cols = " ,".join(col_names)
        query = "SELECT {0} FROM {1}".format(cols, table)

        try:
            cursor.execute(query)
            data = cursor.fetchone()
            return data

            

        except Exception as e:
            print(e)
            return False
    
    def get_data(self, table, col_names=[]):
        cursor = self.connection.cursor(buffered=True)

        cols = " ,".join(col_names)
        query = "SELECT {0} FROM {1}".format(cols, table)

        try:
            cursor.execute(query)
            data = cursor.fetchall()
            return data

            

        except Exception as e:
            print(e)
            return False
        
    def get_data(self, transformation={}):
        time_format = "%Y-%m-%d %H:%M:%S.%f%z"
        table = transformation['table']
        col_names = []
        for key_col in transformation['mapping']:
            col_names.append(transformation['mapping'][key_col])

        cursor = self.connection.cursor(buffered=True)

        cols = " ,".join(col_names)
        query = "SELECT {0} FROM {1}".format(cols, table)

        try:
            cursor.execute(query)
            data = cursor.fetchall()
            result = []

            for dt in data:

                date_string = dt[0]

                if '.' in date_string:
                    parts = date_string.split('.')
                    date_string = parts[0] + '.' + parts[1][:6]

                # Parse the string into a datetime object
                datetime_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")

                unix_timestamp = datetime_obj.timestamp()

                result.append((unix_timestamp, dt[1]))

            return result

            
        except Exception as e:
            print(e)
            return False
       
    
    def post_data(self, fields=[]):
        return 1
    
    def describe_db(self):
        cursor = self.connection.cursor(buffered=True)

        # Execute a query to retrieve table information
        cursor.execute("SHOW TABLES")

        # Fetch all the table names
        tables = cursor.fetchall()

        response = []
        # Print the list of tables
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            response.insert(0, {"table_name": table_name})

            response[0]['cols'] = []

            # Get the columns for each table
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            for column in columns:
                col = {"name": column[0], "type": str(column[1]), "null": str(column[2]), "key": str(column[3]), "default": str(column[4]) }
                response[0]['cols'].append(col)

                print(col)

        # Close the cursor and connection
        cursor.close()

        return jsonify(response)