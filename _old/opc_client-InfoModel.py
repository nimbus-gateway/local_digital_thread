import asyncio
import logging
import asyncua

from asyncua import ua, Client

from app.metadata.metadata import MetaData
from app.connectors.mysql_connector import MySQLConnector
import os
from app.config.config import Config


client = Client("opc.tcp://localhost:4840/freeopcua/server/")

cwd = os.path.abspath('./')
mapping = MetaData(cwd + '/app/metadata/mapping.json')

config_instance = Config("app/config/config.yaml")
opc_config = config_instance.get_opc_config()
db_config = config_instance.get_database_config()


sql = MySQLConnector('energymeters', db_config['host'], db_config['username'], db_config['password'])

NodeClass = asyncua.ua.attribute_ids.AttributeIds

async def get_variable_node_id(object_node_id, variable_name):
    await client.connect()

    object_node = client.get_node(object_node_id)

    # Get the children of the object node.
    children_nodes = await object_node.get_children()

    # Iterate over the children nodes and find the node for the variable.
    for child_node in children_nodes:
        if child_node.node_class == NodeClass.Variable and child_node.browse_name == variable_name:
            variable_node = child_node
            break

    # Get the nodeid of the variable node.
    variable_node_id = variable_node.node_id

    # Close the OPCUA client.
    await client.disconnect()

    return variable_node_id



async def main():
    try:
        await client.connect()

        # root = client.get_root_node()

        # print("Object node is ", root)


        # print("Children of root are :", await root.get_children())

        # print("Desription of childrens are :", await root.get_children_descriptions())




        # data_map = mapping.get_nodes()

        data_map = [{"nodeid":65}, {"nodeid":87}]
        print(data_map)
        for item in data_map:

            nodeid = int(item["nodeid"])

            node_object_id = "ns={0};i={1}".format(2, nodeid)

            node_object = client.get_node(node_object_id)

            node_object_id = "ns={0};i={1}".format(2, nodeid+4)
            Measurementvalue = client.get_node(node_object_id)


            await Measurementvalue.write_value(0.232)
            variable_name = "Measurementvalue"
            # variable_node_id = await get_variable_node_id(node_object_id, variable_name)

            # print(variable_node_id)
            # value_variable = await node_object.get_child("2:Measurementvalue")


            # print(timestamp_variable)
            # print(value_variable.nodeid)

            # result = sql.get_latest_data(item["Table"], [item['TimeStamp'], item["Value"]])

            # print("Result from SQL :", result)
            # await timestamp_variable.set_value(result[0])

            # await value_variable.set_value(ua.DataValue(float(0.001)))




        

    finally:
        await client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())