import csv
import mysql.connector


# Connect to the database
connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="admin",
    database="energymeters",
    auth_plugin='mysql_native_password'
)


cursor = connection.cursor()

# Read data from CSV file
csv_file_path = 'sample data/block_13_portion.csv'
with open(csv_file_path, 'r') as file:
    reader = csv.reader(file)
    
    # Skip header row (if any)
    next(reader)
    
    for row in reader:
        # Convert string values to float for the specified columns
        row[2:] = [float(value) if value else None for value in row[2:]]
        
        query = """
        INSERT INTO block_13 
        (LCLid, tstp, energy) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, row)

# Commit the changes
connection.commit()

# Close the connection
cursor.close()
connection.close()
