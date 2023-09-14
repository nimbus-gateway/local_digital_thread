from opcua import Client
from app.mapping.mapping import Mapping
from app.connectors.mysql_connector import MySQLConnector
import os
from app.config.config import Config


client = Client("opc.tcp://localhost:4840/freeopcua/server/")

cwd = os.path.abspath('./')
mapping = Mapping(cwd + '/app/mapping/mapping.json')

config_instance = Config("app/config/config.yaml")
opc_config = config_instance.get_opc_config()
db_config = config_instance.get_database_config()


sql = MySQLConnector('energymeters', db_config['host'], db_config['username'], db_config['password'])






try:
    client.connect()

    root = client.get_root_node()

    print("Object node is ", root)


    print("Children of root are :", root.get_children())

    print("Desription of childrens are :", root.get_children_descriptions())




    data_map = mapping.get_datamap()

    for item in data_map:

        nodeid = int(item["nodeid"])

        node_object_id = "ns={0};i={1}".format(2, nodeid)

        node_object = client.get_node(node_object_id)

        timestamp_variable = node_object.get_child("2:TimeStamp")
        value_variable = node_object.get_child("2:Value")

        print(timestamp_variable.nodeid)

        result = sql.get_latest_data(item["Table"], [item['TimeStamp'], item["Value"]])


        timestamp_variable.set_value(result[0])

        value_variable.set_value(result[1])




    

finally:
    client.disconnect()
