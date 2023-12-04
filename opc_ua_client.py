import asyncio
import logging
import os
from app.metadata.metadata import MetaData
from app.connectors.MySQL import MySQL
from app.config.config import Config
from comms.coms import RestClient
import importlib
import traceback
from datetime import datetime, timedelta
import argparse


from asyncua import Client, ua



# LOCAL DIGITAL THREAD VARIABLES
config_instance = Config("app/config/config.yaml")
opc_config = config_instance.get_opc_config()
api_config = config_instance.get_api_config()
dt_api = RestClient("http://{0}:{1}/".format(api_config['host'], api_config['port']))



_logger = logging.getLogger(__name__)


# Create the parser
parser = argparse.ArgumentParser(description="OPC UA Data Ingestion Client Script for DBs.")


# Add an argument
parser.add_argument('--opcua_reference_id', type=str, help="this is ")
parser.add_argument('--all', action='store_true', help="A boolean flag. If present, stores True, otherwise False.")

# Parse the arguments
args = parser.parse_args()

# sql = MySQLConnector('energymeters', db_config['host'], db_config['username'], db_config['password'])

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("New data change event", node, val)

    def event_notification(self, event):
        print("New event", event)

def unix_timestamp_to_ua_datetime(unix_timestamp):
    """
    Converts a Unix timestamp to an OPC UA DateTime object.
    
    Args:
    unix_timestamp (float): The Unix timestamp to convert.

    Returns:
    ua.DateTime: The corresponding OPC UA DateTime object.
    """
    # Convert Unix timestamp (seconds since 1970-01-01) to OPC UA DateTime format
    # OPC UA DateTime starts from 1601-01-01
    unix_epoch = datetime(1970, 1, 1)
    ua_epoch = datetime(1601, 1, 1)
    delta_to_unix_epoch = unix_epoch - ua_epoch
    total_seconds = delta_to_unix_epoch.total_seconds() + unix_timestamp
    # OPC UA DateTime is in 100-nanosecond intervals
    opcua_intervals = int(total_seconds * 10**7)

    return ua.DateTime(opcua_intervals)

async def main():
    url = "opc.tcp://localhost:4840/freeopcua/server/"
    async with Client(url=url) as client:
        _logger.info("Root node is: %r", client.nodes.root)
        _logger.info("Objects node is: %r", client.nodes.objects)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        _logger.info("Children of root are: %r", await client.nodes.root.get_children())

        uri = "http://examples.freeopcua.github.io"
        idx = await client.get_namespace_index(uri)
        _logger.info("index of our namespace is %s", idx)



        response = dt_api.get('nodes')

        if response.status_code == 200:
            nodes = response.json()
            _logger.info("Response from API:  %r", nodes)
        else:
            _logger.error("Data Transformation API returins: %r", response.status_code)
            exit()

        #iterating through OPC UA nodes

        if args.all:
            nodes = nodes
        else:

            nodes = {args.opcua_reference_id: nodes[str(args.opcua_reference_id)]}
            print(nodes)

        for key in nodes:
            node = nodes[key]
            measurementtimestamp_nid= node['MeasurementTimeStamp']['nodeid']
            measurementvalue_nid = node['Measurementvalue']['nodeid']
            transformation = node["Transformation"]

            nodeid = node['nodeid']

            print(nodeid)

            actual_data_points = {}


            connector_id = transformation['connector']

            _logger.info("Getting info on data source:  %r", connector_id)
            response = dt_api.get('datasource/'+ connector_id)

            print(response.json())

            if response.status_code == 200:
                con = response.json()

                try:
                    module_name = "app.connectors.{0}".format(con['connector'])
                    print(module_name)
                    module = importlib.import_module(module_name)

                    Connector = getattr(module, con['connector'])
                    
                    connector = Connector()

                    print(transformation)
                    # print(connector)
                    status = connector.connect(transformation, con['connection_profile'])
                    
                    if status:
                        _logger.info("Connection initialized using")

                        resp = connector.get_data(transformation=transformation)
                        print("here.............,")
                        print(resp)
                        
                        if resp:
                            _logger.info("Raw data received")

                            

                            opc_value_variable = client.get_node(ua.NodeId(int(measurementvalue_nid), 2))
                            opc_time_variable = client.get_node(ua.NodeId(int(measurementtimestamp_nid), 2))
                            _logger.info("opc_value_nodeid is: %r", measurementvalue_nid)
                            _logger.info("opc_timestamp_nodeid is: %r", measurementtimestamp_nid)
                            _logger.info("opc_value_variable is: %r", opc_value_variable)
                            _logger.info("opc_time_variable is: %r", opc_time_variable)

                            for val in resp:
                                print(val[1])

                                data_value = ua.DataValue(ua.Variant(float(val[1]), ua.VariantType.Double), SourceTimestamp = datetime.utcfromtimestamp(val[0])) 

                                # await opc_value_variable.write_value(float(val[1]))
                                await opc_value_variable.write_value(data_value)


                                await opc_time_variable.write_value(datetime.utcfromtimestamp(val[0]))

                                val = await opc_value_variable.read_value()
                                date = await opc_time_variable.read_value()

                    else:
                        _logger.error("Connection Failed")



                except Exception as e:
                    
                    _logger.error("Error During Connection %r", e)
                    print(traceback.format_exc())
                    exit()
            else:
                _logger.error("Connector Not registered :  %r", connector_id)
                continue

            
        # result = sql.get_latest_data(item["Table"], [item['TimeStamp'], item["Value"]])

        # print("Result from SQL :", result)

        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        #var = client.get_node("ns=3;i=2002")
        #print(var)
        #await var.read_data_value() # get value of node as a DataValue object
        #await var.read_value() # get value of node as a python builtin
        #await var.write_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        #await var.write_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path
       # myvar = await client.nodes.root.get_child(["0:Objects", "2:West Wing Building", "2:BuildingID"])
        # myvar = client.get_node(ua.NodeId(67, 2))
        # # obj = await client.nodes.root.get_child(["0:Objects", "2:West Wing Building"])
        # _logger.info("myvar is: %r", myvar)
        
        # await myvar.write_value(3.9)

        # val = await myvar.read_value()
        # print(val)


        # subscribing to a variable node
        # handler = SubHandler()
        # sub = await client.create_subscription(10, handler)
        # handle = await sub.subscribe_data_change(test)
        # await asyncio.sleep(0.1)

        # we can also subscribe to events from server
        # await sub.subscribe_events()
        # await sub.unsubscribe(handle)
        # await sub.delete()

        # calling a method on server
        # res = await obj.call_method("2:multiply", 3, "klk")
        # _logger.info("method result is: %r", res)
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())