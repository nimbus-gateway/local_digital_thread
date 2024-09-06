import json
from flask import jsonify
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
import traceback
import asyncio


import sys
sys.path.append("..")

_logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod
class Connector:
    def __init__(self,):
        self.connection = None
        # self.dbname = dbname

    @abstractmethod
    def connect(self, transformation={}, connection_profile={}):
        pass

    @abstractmethod
    def get_data(self, transformation={}):
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




class MQTT(Connector):
    def __init__(self):
        super().__init__()
        self.client = None
        self.transformation = None
        # Buffer to hold incoming MQTT messages
        self.mqtt_buffer = asyncio.Queue()

    def connect(self, transformation={}, connection_profile={}):
        _logger.info("MQQT: Inititalizing the connection")
        _logger.info("MQQT: Connection Profile:" + str(connection_profile))
        _logger.info("MQQT: Transformation Profile:" + str(transformation))
        self.transformation = transformation
        return self.connect_(connection_profile['host'], int(connection_profile['port']), connection_profile['username'], connection_profile['password'])

    def connect_(self, host, port, username, password):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        if username and password:
            self.client.username_pw_set(username, password)

        status = self.client.connect(host, port)
        print("MQQT connecttion status : " + str(status))
        if not status == mqtt.MQTT_ERR_SUCCESS:
            return False
        # Rest of your connection logic
        _logger.info(f"Connected to MQTT broker at {host}")
        return True
    
    def get_buffer(self):
        """
        Return the mqqt buffer 
        """
        return self.mqtt_buffer	
    
    def on_message(self, client, userdata, message):
        """
        Callback function when a message is received on the subscribed topic.
        Decodes and processes the message payload.
        """
        try:
            decoded_message = message.payload.decode("utf-8")
            # print(f"Received message '{decoded_message}' on topic '{message.topic}'")
            message_dict = json.loads(decoded_message)
            # print("Decoded message as JSON:", message_dict)

            # Add the message to the async buffer
            # self.mqtt_buffer.put(decoded_message)
            asyncio.run_coroutine_threadsafe(self.mqtt_buffer.put(decoded_message), loop=asyncio.get_event_loop())

            # Process the message here if needed (e.g., parse JSON, etc.)
        except Exception as e:
            print(f"Error Occured on MQQT Callback: {e}")


    def get_data(self, transformation={}):
        _logger.info("Attempting Retrieve Data From MQQT Broker")
        time_format = transformation['mapping']['TimeFormat']
        topic = transformation['topic']
        _map = transformation['mapping']
        del _map['TimeFormat']

        try:
            self.client.on_message = self.on_message
            self.client.subscribe(topic)
            _logger.info(f"Subscribed to topic: {topic}")
            print(f"Subscribed to topic: {topic}")
            self.client.loop_start() 

        except Exception as e:
            _logger.error("An error occurred when getting data: %s", str(e))
            _logger.error("Stack trace:\n%s", traceback.format_exc())
            print("Stack trace:\n%s", traceback.format_exc())
            return False



       

    def post_data(self, fields=[]):
        for topic, data in fields.items():
            self.client.publish(topic, data)
            _logger.info(f"Published data to topic {topic}: {data}")

    def describe_table(self, table_name):
        raise NotImplementedError("describe_table method is not applicable to MQTT.")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        _logger.info("Disconnected from MQTT broker")
