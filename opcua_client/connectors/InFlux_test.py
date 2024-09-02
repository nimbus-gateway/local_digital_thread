import unittest
from unittest.mock import patch, MagicMock
from InFlux import InFlux  # replace 'your_module' with the name of your module

class TestInFlux(unittest.TestCase):

    def setUp(self):
        self.influx = InFlux()

    @patch('InFlux.influxdb_client.InfluxDBClient')
    def test_connect_(self, mock_client):
        # Test successful connection
        self.assertTrue(self.influx.connect_("mtu", "localhost", "8086", "6R9Hg8swLRMBSVn6swE6yqmXAhSdcHAZ_G73NjP6QhdQKUkYhZWEuRfP-WsDKg5A3aYSnpBzmcG4fkUEoxZeGQ=="))
        # You may also want to check if InfluxDBClient was called with the right arguments
        
        # Test connection failure
        # mock_client.side_effect = Exception("Connection Failed")
        # self.assertFalse(self.influx.connect_("org", "host", "port", "token"))

    def test_connect(self):

        mapping={}
        connection_profile={"org":"mtu", "host": "localhost", "port":"8086", "token":"6R9Hg8swLRMBSVn6swE6yqmXAhSdcHAZ_G73NjP6QhdQKUkYhZWEuRfP"}

    
        self.assertTrue(self.influx.connect(mapping=mapping, connection_profile=connection_profile))


    def test_get_data(self):
        # Mock the cursor method and its return values to test get_data (SQL version)
        mapping ={"bucket": "local_digital_thread", "field": "power_consumption", "measurement": "test_B"}
        connection_profile={"org":"mtu", "host": "localhost", "port":"8086", "token":"6R9Hg8swLRMBSVn6swE6yqmXAhSdcHAZ_G73NjP6QhdQKUkYhZWEuRfP"}

        self.influx.connect(mapping=mapping, connection_profile=connection_profile)

        self.assertTrue(self.influx.get_data(mapping=mapping))

    # def test_disconnect(self):
    #     # Test if disconnect calls the right method in the InfluxDB client
    #     pass

    # @patch('your_module.InFlux.connection')
    # def test_get_latest_data(self, mock_connection):
    #     # Mock the cursor method and its return values to test get_latest_data
    #     pass

    # @patch('your_module.InFlux.connection')
    # def test_get_data(self, mock_connection):
    #     # Mock the cursor method and its return values to test get_data (SQL version)
    #     pass

    # @patch('your_module.InFlux.connection')
    # def test_get_data_influx(self, mock_connection):
    #     # Mock the query_api and its return values to test get_data (InfluxDB version)
    #     pass

    # def test_post_data(self):
    #     # Depending on what post_data is supposed to do, write tests for it
    #     pass

    # @patch('your_module.InFlux.connection')
    # def test_describe_db(self, mock_connection):
    #     # Mock the cursor and its methods to test describe_db
    #     pass

if __name__ == '__main__':
    print("test")
    inf = InFlux()


    t = inf.connect_("mtu", "localhost", "8086", "XV4s3wRVDd4_D2snazc1YQifzEFLog91MIMnM1Xq7BpYI8uE5gTzYUtIjVEFHDGpblyfyHIRMjczjN5QKxHWmw==")
    print(t)
    transformation ={ "connector": "connector_influx_local01",
                "dbname": "local_digital_thread",
                "mapping": {
                    "MeasurementTimeStamp": "time",
                    "Measurementvalue": "power_consumption"
                },
                "mapping_type": "database",
                "table": "test_B"}

    result = inf.get_data(transformation=transformation)
    print(result)

    # inf.describe_db('local_digital_thread', 'test_B')

    # print(t)
    # unittest.main()