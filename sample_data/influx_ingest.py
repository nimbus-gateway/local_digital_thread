import pandas as pd
from influxdb import InfluxDBClient
from datetime import datetime

# The path to your CSV file
csv_file_path = 'ieee_hotel_data.csv'

# InfluxDB connections settings
host = 'localhost'
port = 8086
user = 'admin'
password = 'influxadmin'
dbname = 'test'

# Create an instance of the InfluxDB client
client = InfluxDBClient(host, port, user, password, dbname)

# Load your CSV file as a pandas DataFrame
data = pd.read_csv(csv_file_path, sep=',')

# Convert the Time column to datetime objects assuming the format in your CSV

data['Time'] = pd.to_datetime(data['Time'], format='%m/%d/%Y %I:%M %p')

# Prepare data for InfluxDB
points = []
for i, row in data.iterrows():
    points.append({
        "measurement": "meter_b",
        "time": row['Time'].isoformat(),
        "fields": {
            "power_consumption": row['power consumption'],
            "temperature": row['temperature'],
            "humidity": row['humidity'],
            "speed": row['speed(KM/H)']
        }
    })

# Write points to InfluxDB
client.write_points(points)

# Close client connection
client.close()