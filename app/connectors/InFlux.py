import json
import mysql
from mysql import connector
from flask import jsonify
import logging
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
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

class InFlux(Connector):
    def __init__(self):
        self.connection = None
        self.org = None

    def connect_(self, org, host, port, token):
        try:
            _logger.info("Influx: Inititalizing the connection")
            token = token
            org =  org
            url = "http://{}:{}".format(host, port)

            self.connection = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
            self.org = org
            _logger.info("Inflix connection success")

            return True
        except Exception as e:
            _logger.error("Error Occured")
            print(e)
            return False
        
    def connect(self, transformation={}, connection_profile={}):

        _logger.info("Influx: Inititalizing the connection")
        return self.connect_(connection_profile['org'], connection_profile['host'], connection_profile['port'], connection_profile['token'])

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
    

        
    def get_data(self, transformation={}):

        _logger.info("Argument Recieved get_data", transformation)

        bucket = transformation['dbname']
        fieled_name = transformation['mapping']['Measurementvalue'] 
        measurement = transformation['table']
        time_format = "%Y-%m-%d %H:%M:%S.%f%z"
        query_api = self.connection.query_api()

        query = """from(bucket: "{0}")
        |> range(start: -5h)
        |> filter(fn: (r) => r["_field"] == "{1}")
        |> filter(fn: (r) => r._measurement == "{2}")""".format(bucket, fieled_name, measurement)


        try:
            tables = query_api.query(query, org=self.org)
            result = []
            for table in tables:
                for record in table.records:
                    
                    datetime_obj = record['_time']
                    unix_timestamp = datetime_obj.timestamp()

                    result.append((unix_timestamp, record['_value']))

            print(result)
            return result

            
        except Exception as e:
            print(e)
            return False
       
    
    def post_data(self, fields=[]):
        return 1
    
    def describe_db(self, bucket, measurement):

        query_field_keys = """
                    import "influxdata/influxdb/schema"

                    schema.measurementFieldKeys(bucket: "{0}", measurement: "{1}")
                    """.format(bucket, measurement)
        
        
        query_api = self.connection.query_api()

        result_field_keys = query_api.query(org=self.org, query=query_field_keys)

        tables_columns = result_field_keys[0].records

        print(type(tables_columns))

        cols = []
        for val in tables_columns:
            cols.append(val.values)

        # json_output = json.dumps(cols)
        print(cols)
        return jsonify(cols)