import unittest
import time
from unittest.mock import patch
from MQQT import MQTT  # Assuming your implementation is in mqtt_connector.py

class TestMQTT(unittest.TestCase):

    def setUp(self):
        self.mqtt_connector = MQTT()
        self.broker = '127.0.0.1'
        self.port = 1883
        self.topic = 'sensor/opied1/synthetic_data'
        self.transformation = {
                                    "mapping_type": "mqqt",
                                    "connector": "0d99a7cf-b5cc-4a55-8d9d-481a9c9accba",
                                    "topic": "sensor/opied1/synthetic_data",
                                    "mapping": {
                                        "MeasurementTimeStamp": "dateTime",
                                        "Measurementvalue": "deviceValue",
                                        "TimeFormat": "%Y-%m-%d %H:%M:%S.%f"
                                    }
                                }

    def test_connect_(self):
        """Test the connect_ method."""
        
        result = self.mqtt_connector.connect_(self.broker, self.port, "", "")
        self.assertTrue(result)


    def test_get_data(self):
        """Test the get_data method."""

        result = self.mqtt_connector.connect_(self.broker, self.port, "", "")
        self.assertTrue(result)

        self.mqtt_connector.get_data(self.transformation)



    #     self.mqtt_connector.connect_(self.broker, self.port)
    #     mock_subscribe.return_value = (0, 1)  # Simulate successful subscription
    #     callback = MagicMock()
    #     self.mqtt_connector.get_data(self.topic, callback)
    #     mock_subscribe.assert_called_once_with(self.topic)
    #     mock_message_callback_add.assert_called_once_with(self.topic, callback)
    #     self.mock_logger.info.assert_called_with(f"Subscribed to topic {self.topic} with callback {callback}")



    # @patch('paho.mqtt.client.Client.publish')
    # def test_post_data(self, mock_publish):
    #     """Test the post_data method."""
    #     data = "test_message"
    #     mock_publish.return_value = (0, 1)  # Simulate successful publish
    #     self.mqtt_connector.connect_(self.broker, self.port)
    #     self.mqtt_connector.post_data(self.topic, data)
    #     mock_publish.assert_called_once_with(self.topic, data)
    #     self.mock_logger.info.assert_called_with(f"Published data to {self.topic}: {data}")

    # @patch('paho.mqtt.client.Client.subscribe')
    # @patch('paho.mqtt.client.Client.message_callback_add')
    # def test_get_data(self, mock_message_callback_add, mock_subscribe):
    #     """Test the get_data method."""
    #     self.mqtt_connector.connect_(self.broker, self.port)
    #     mock_subscribe.return_value = (0, 1)  # Simulate successful subscription
    #     callback = MagicMock()
    #     self.mqtt_connector.get_data(self.topic, callback)
    #     mock_subscribe.assert_called_once_with(self.topic)
    #     mock_message_callback_add.assert_called_once_with(self.topic, callback)
    #     self.mock_logger.info.assert_called_with(f"Subscribed to topic {self.topic} with callback {callback}")

    # @patch('paho.mqtt.client.Client.disconnect')
    # def test_disconnect(self, mock_disconnect):
    #     """Test the disconnect method."""
    #     self.mqtt_connector.connect_(self.broker, self.port)
    #     self.mqtt_connector.disconnect()
    #     mock_disconnect.assert_called_once()
    #     self.mock_logger.info.assert_called_with("Disconnected from MQTT Broker")

    def tearDown(self):
        self.mqtt_connector.disconnect()

if __name__ == '__main__':

    tm = TestMQTT()
    tm.setUp()
    tm.test_connect_()
    tm.test_get_data()
    # unittest.main()