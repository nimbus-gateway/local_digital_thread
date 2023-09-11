
from opcua import Server, ua
from opcua.common.xmlexporter import XmlExporter
import mysql
from mysql import connector
from datetime import datetime

from rest.model_config import ModelConfig

# Create a server instance
server = Server()

# Set server endpoint URL and port
url = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
server.set_endpoint(url)

server.set_server_name("Energy_Meters_Server")

# Setup server namespace
uri = "http://example.org"
idx = server.register_namespace("OPCUA_SERVER")

# Create a new node for the namespace
root = server.nodes.objects.add_object(idx, "MyServer")

#Define a common object type for energy meter
common_energy_meter_type = server.nodes.base_object_type.add_object_type(idx, "CommonEnergyMeter")


print("Object type id of common energy meter", common_energy_meter_type.nodeid)

#Define common attributes for all energy meter types
time_variable = common_energy_meter_type.add_variable(idx, "TimeStamp", datetime.now())
energy_variable = common_energy_meter_type.add_variable(idx, "Energy", 0.0)


time_variable.set_writable()
energy_variable.set_writable()
# power_variable = common_energy_meter_type.add_variable(idx, "Power", 0.0).set_modelling_rule(True)
#energy_variable = common_energy_meter_type.add_variable(idx, "Energy", 0.0)


#connect to the sql database
connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="admin",
    database="energymeters",
    auth_plugin='mysql_native_password'
)
cursor = connection.cursor(buffered=True)

# Create object types and variables for each table
tables_to_browse = ["block_13"]  # Add your table names here
energy_meter_a = root.add_object(idx, "metera", objecttype=common_energy_meter_type)
# energy_meter_b = root.add_object(idx, "meterb", objecttype=common_energy_meter_type)
# energy_meter_c = root.add_object(idx, "meterc", objecttype=common_energy_meter_type)


server.start()

model_config = ModelConfig()
model_config.load_mapping()


print(model_config.mapping)

try:

    data = model_config.mapping

   
    # query_meter_a = "SELECT tstp, energy FROM block_13"
    # cursor.execute(query_meter_a)
    # data_meter_a = cursor.fetchall()

    # date_format = "%Y-%m-%d %H:%M:%S"
    

    # for row in data_meter_a:

    #     base_date, extra_digit = row[0].rsplit('.', 1)

    #     print(base_date)
    #     dt = date_object = datetime.strptime(base_date, date_format)

    #     energy_meter_a.get_child(["2:TimeStamp"]).set_value(dt)
    #     energy_meter_a.get_child(["2:Energy"]).set_value(row[1])
    


    server.export_xml_by_ns('Energy_meter_Model.xml',namespaces="OPCUA_SERVER")

except KeyboardInterrupt:
    server.stop()
    connection.close()


# try:
#     while True:
#         # Retrieve data and update variables for energy_ameter_a
#         query_meter_a = "SELECT tstp, energy FROM block_13"
#         cursor.execute(query_meter_a)
#         data_meter_a = cursor.fetchone()

#         date_format = "%Y-%m-%d %H:%M:%S.%f"
#         print(data_meter_a[0])
#         break
#         date_object = datetime.strptime(data_meter_a[0], date_format)

#         energy_meter_a.get_child(["2:TimeStamp"]).set_value(date_object)
#         energy_meter_a.get_child(["2:Energy"]).set_value(data_meter_a[1])


#         # Retrieve data and update variables for energy_ameter_b
#         # query_meter_b = "SELECT Voltage, Current, Power FROM meterb"
#         # cursor.execute(query_meter_b)
#         # data_meter_b = cursor.fetchone()

#         # energy_meter_b.get_child(["2:Voltage"]).set_value(data_meter_b[0])
#         # energy_meter_b.get_child(["2:Current"]).set_value(data_meter_b[1])
#         # energy_meter_b.get_child(["2:Power"]).set_value(data_meter_b[2])

#         # Retrieve data and update variables for energy_ameter_c
#         # query_meter_c = "SELECT Phase_A_voltage, Phase_B_voltage, Phase_C_voltage, Current, Active_Power FROM meterc"
#         # cursor.execute(query_meter_c)
#         # data_meter_c = cursor.fetchone()

#         # energy_meter_c.get_child(["2:Voltage"]).set_value(data_meter_c[0]+data_meter_c[1]+data_meter_c[2])
#         # energy_meter_c.get_child(["2:Current"]).set_value(data_meter_c[3])
#         # energy_meter_c.get_child(["2:Power"]).set_value(data_meter_c[4])
                    
# except KeyboardInterrupt:
#     server.stop()
#     connection.close()


