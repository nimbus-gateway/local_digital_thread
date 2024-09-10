import sys
import json
import datetime
import time
import random
import logging
from influxdb_client import InfluxDBClient, Point, WritePrecision

# Logger
logger = logging.getLogger(__name__)

# Seed for random generation
random.seed(0)

# Global vars
DEVICE_NAME = 'OPIED02'
T = 2  # data period

# InfluxDB configurations
INFLUXDB_URL = 'http://192.168.76.220:32415/'  # Replace with your InfluxDB URL
INFLUXDB_TOKEN = 'DxaqjPiiTRMyD6BUZB6LmIr9DRCXQm7FliJQJpa64B-AxTU1C1fFhoQI9tISRvV3Nktwm-RUtWShtf5Y634oNQ=='  # Replace with your InfluxDB token
INFLUXDB_ORG = 'mtu'  # Replace with your organization name in InfluxDB
INFLUXDB_BUCKET = 'BMS'  # Replace with the bucket name in InfluxDB

# InfluxDB client initialization
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api()

# Generate random sensor data
def gen_rnd_sensor_data(low: float, high: float) -> float:
    return random.uniform(low, high)

# Generate Temperature values
def getTemperatureValues():
    data = {}
    data['powerConsumption'] = gen_rnd_sensor_data(15, 35)
    data['deviceParameter'] = 'Temp'
    data['deviceId'] = DEVICE_NAME
    data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

try:
    print(f'Connecting to InfluxDB at {INFLUXDB_URL}')
    
    while True:
        print("In the loop")

        # Generate sensor data
        data = getTemperatureValues()

        # Create an InfluxDB point
        point = Point("sensor_data") \
            .tag("deviceId", data['deviceId']) \
            .field("powerConsumption", data['powerConsumption']) \
            .field("deviceParameter", data['deviceParameter']) \
            .time(datetime.datetime.utcnow(), WritePrecision.NS)

        # Write the point to InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

        print(f"Published {data} to InfluxDB at {time.asctime()}")
        logger.info(f"Published {data} to InfluxDB at {time.asctime()}")

        time.sleep(T)

except KeyboardInterrupt:
    print("Terminated by user")
finally:
    # Close the InfluxDB client
    client.close()
