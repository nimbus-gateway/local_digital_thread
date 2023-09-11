from opcua import Client
from rest.mapping.mapping import Mapping
from rest.connectors.mysql_connector import MySQLConnector
import os


client = Client("opc.tcp://localhost:4840/freeopcua/server/")

cwd = os.path.abspath('./')
mapping = Mapping(cwd + '/rest/mapping/mapping.json')

sql = MySQLConnector("energymeters")





try:
    client.connect()

    root = client.get_root_node()

    print("Object node is ", root)


    print("Children of root are :", root.get_children())

    print("Desription of childrens are :", root.get_children_descriptions())


    node = client.get_node("ns=2;i=79") 

    value_to_write = 42

    node.set_value(value_to_write)


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
