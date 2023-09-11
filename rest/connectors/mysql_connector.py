import json
import mysql
from mysql import connector
from flask import jsonify

from abc import ABC, abstractmethod
class Connector:
    def __init__(self, dbname):
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



class MySQLConnector(Connector):
    def __init__(self, dbname):
        self.connection = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    password="admin",
                    database= dbname,
                    auth_plugin='mysql_native_password'
                )
    
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