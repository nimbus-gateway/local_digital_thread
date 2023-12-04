import pandas as pd
import mysql.connector
from datetime import datetime

# The path to your CSV file
csv_file_path = 'auxiliary_services.csv'

# MySQL database connection configuration
config = {
    'user': 'root',
    'password': 'admin',
    'host': '127.0.0.1',
    'database': 'energymeters',
    'raise_on_warnings': True
}

# Create a connection object
connection = mysql.connector.connect(**config)
cursor = connection.cursor()

# Create a table (if it does not already exist)
create_table_query = '''
CREATE TABLE IF NOT EXISTS MeterData (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tagname VARCHAR(255),
    power FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    speed FLOAT,
    time DATETIME
)
'''
cursor.execute(create_table_query)

# Load your CSV file as a pandas DataFrame
data = pd.read_csv(csv_file_path, sep=',')

# Convert the Time column to datetime objects assuming the format in your CSV
data['Time'] = pd.to_datetime(data['Time'], format='%m/%d/%Y %H:%M')


# Prepare the INSERT INTO statement
insert_query = '''
INSERT INTO MeterData (tagname, power, temperature, humidity, speed, time)
VALUES (%s, %s, %s, %s, %s, %s)
'''

for i, row in data.iterrows():
    # Create a tuple of the values to be inserted
    values_to_insert = (
        'meterA',  # Assuming tagname is fixed, as per your InfluxDB code
        float(row['power consumption']),
        float(row['temperature']),
        float(row['humidity']),
        float(row['speed(KM/H)']),
        row['Time'].to_pydatetime()  # Convert the Timestamp to a datetime object
    )
    
    # Execute the query
    cursor.execute(insert_query, values_to_insert)

    # Optionally, you can commit after each insert, or do it once after the loop ends
    # connection.commit()

# Commit the transaction
connection.commit()

# Close the cursor and connection
cursor.close()
connection.close()