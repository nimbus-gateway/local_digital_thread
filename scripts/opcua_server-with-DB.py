from opcua import Server, ua
import mysql
from mysql import connector

i=0
# Create a server instance
server = Server()

# Set server endpoint URL and port
url = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
server.set_endpoint(url)

server.set_server_name("Energy Model Server")

# Setup server namespace
uri = "http://example.org"
idx = server.register_namespace(uri)

# Create a new node for the namespace
root = server.nodes.objects.add_object(idx, "MyServer")

connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="admin",
    database="energy_data"
)
cursor = connection.cursor(buffered=True)
#cursor = cnx.cursor(buffered=True)
# Start the server
server.start()

#Define custom object types and variables for each table
table_data_objects = {}

def create_object_type_and_variables(table_name):
    table_data_object = server.nodes.base_object_type.add_object_type(idx, f"{table_name}ObjectType")

    table_data_objects[table_name] = root.add_object(idx, f"{table_name}", objecttype=table_data_object)
    columns = get_table_columns(table_name)
    
    for column in columns:
        table_data_objects[table_name].add_variable(idx, column,"").set_modelling_rule(True)
    

def get_table_columns(table_name):
    cursor.execute(f"SELECT * FROM {table_name} WHERE 1=0")  # Retrieve the table structure
    return [column[0] for column in cursor.description]

# Create object types and variables for each table
tables_to_browse = ["energy", "machines"]  # Add your table names here
for table_name in tables_to_browse:
    create_object_type_and_variables(table_name)


server.export_xml_by_ns('Energy_Server_Model.xml',namespaces="Energy Model Server")

# Add object instances to the address space and push data
try:
    while True:
        for table_name in tables_to_browse:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()

            #table_data_object = table_data_objects[table_name]
            variables = table_data_objects[table_name].get_variables()

            for row in data:
                #obj = server.nodes.objects.add_object(2, f"{table_name}_{row[0]}")
                #obj.set_type(table_data_object)
                for i, column_value in enumerate(row):
                    variables[i].set_value(column_value)
                 #   obj.add_variable(2, variables[i].get_browse_name().Name, column_value)
           # server.publish_objects()

except KeyboardInterrupt:
    pass
finally:
    server.stop()
    connection.close()