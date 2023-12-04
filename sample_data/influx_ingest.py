import pandas as pd
from influxdb import InfluxDBClient
from datetime import datetime

# The path to your CSV file
csv_file_path = 'ieee_hotel_data.csv'


import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN")
org = "mtu"
url = "http://localhost:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token="XV4s3wRVDd4_D2snazc1YQifzEFLog91MIMnM1Xq7BpYI8uE5gTzYUtIjVEFHDGpblyfyHIRMjczjN5QKxHWmw==", org=org)


bucket="energy_meters"

write_api = write_client.write_api(write_options=SYNCHRONOUS)

# Load your CSV file as a pandas DataFrame
data = pd.read_csv(csv_file_path, sep=',')

# Convert the Time column to datetime objects assuming the format in your CSV

data['Time'] = pd.to_datetime(data['Time'], format='%m/%d/%Y %H:%M')
data['Time'] = data['Time'].apply(lambda x: int(x.timestamp()))


for i, row in data.iterrows():

    point = ( Point("Meter_E")
    .tag("tagname", "meterE")
    .field("power_consumption", float(row['power consumption']))
    .field("temperature", float(row['temperature']))
    .field("humidity", float(row['humidity']))
    .field("speed", float(row['speed(KM/H)']))
    .field("time", int(row['Time']))
    .time(int(row['Time']), WritePrecision.S))

    print(point)
    write_api.write(bucket=bucket, org="mtu", record=point)
    # time.sleep(1) # separate points by 1 second
