import json
import mysql
from mysql import connector
from flask import jsonify
import logging
from datetime import datetime
import traceback

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
        _logger.info("Connecting With Data Source: MYSQL")
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
            _logger.error("An error occurred: %s", str(e))
            _logger.error("Stack trace:\n%s", traceback.format_exc())
            print(e)
            return False
    

    def get_data(self, transformation={}):
        _logger.info("Attempting Retrieve Data From MYSQL DB")
        # time_format = "%Y-%m-%d %H:%M:%S.%f"
        time_format = transformation['mapping']['TimeFormat']
        table = transformation['table']
        col_names = []
        _map = transformation['mapping']
        del _map['TimeFormat']
        for key_col in _map:
            col_names.append(_map[key_col])

        cursor = self.connection.cursor(buffered=True)

        cols = " ,".join(col_names)
        query = "SELECT {0} FROM {1}".format(cols, table)

        try:
            cursor.execute(query)
            data = cursor.fetchall()
 
            result = []
            
            if len(data) !=0:
                for dt in data:
                    # date = dt[0]
                    # print(date)
                    # getting the first value as time and creating a datetime object
                    print(dt[0][:-1])
                    date_obj = datetime.strptime(dt[0][:-1], str(time_format))
                    unix_timestamp = date_obj.timestamp()
                    # unix_timestamp = datetime.now().timestamp()

                    result.append((unix_timestamp, dt[1]))

                return result

            else:
                _logger.info("No Data Available")
                return False

            
        except Exception as e:
            _logger.error("An error occurred: %s", str(e))
            _logger.error("Stack trace:\n%s", traceback.format_exc())
            return False
       
    
    def post_data(self, fields=[]):
        return 1
    
    def describe_db(self, table_name):
        cursor = self.connection.cursor(buffered=True)


        response = []
            # Get the columns for each table
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        for column in columns:
            col = {"name": column[0], "type": str(column[1]), "null": str(column[2]), "key": str(column[3]), "default": str(column[4]) }
            response.append(col)

            print(col)

        # Close the cursor and connection
        cursor.close()

        return jsonify(response)