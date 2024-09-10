import sys
import json
import datetime
import time
import random
import paho.mqtt.client as mqtt
import logging

logger = logging.getLogger(__name__)

random.seed(0)



# Global vars
DEVICE_NAME = 'OPIED03'
MQTT_BROKER = '192.168.76.25'
TOPIC = "sensor/smartmeter/nimbus_testbed1"
T = 30  # data period

# MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# Handle will
msg = {
    'msg_type': 'status',
    'status': 'offline',
}
client.will_set(f'{TOPIC}/status', payload=json.dumps(msg), qos=2, retain=True)

# Generate random sensor data
def gen_rnd_sensor_data(low: float, high: float) -> float:
    return random.uniform(low, high)

# generate Temperature values
def getTemperatureValues():
    data = {}
    data['deviceValue'] = gen_rnd_sensor_data(15, 35)
    data['deviceParameter'] = 'Temp'
    data['deviceId'] = DEVICE_NAME
    data['dateTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data


try:
    print(f'Connecting to MQTT broker running on {MQTT_BROKER}')
    client.loop_start()
    client.connect(MQTT_BROKER, 1883, 60)
    while True:
        print("In the loop")

        time.sleep(1)
        data = json.dumps(getTemperatureValues())
        # Publish to the MQTT topic
        client.publish(TOPIC, data, 0)
        print(f"Published {data} to topic {TOPIC} at {time.asctime()}")
        logger.info(f"Published {data} to topic {TOPIC} at {time.asctime()}")
except KeyboardInterrupt:
    print("Terminated by user")
finally:
    # Disconnect from the MQTT broker
    client.disconnect()
