import asyncio
import logging
import os
from app.metadata.metadata import MetaData
from app.connectors.MySQL import MySQL
from app.config.config import Config
from comms.coms import RestClient
import importlib

from asyncua import Client, ua

# LOCAL DIGITAL THREAD VARIABLES
config_instance = Config("app/config/config.yaml")
opc_config = config_instance.get_opc_config()
api_config = config_instance.get_api_config()
dt_api = RestClient("http://{0}:{1}/".format(api_config['host'], api_config['port']))



_logger = logging.getLogger(__name__)

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
            nodes = response.json()['nodes']
            _logger.info("Response from API:  %r", nodes)
        else:
            _logger.error("Data Transformation API returins: %r", response.status_code)
            exit()

        #iterating through OPC UA nodes
        for node in nodes:
            measurementtimestamp = node['MeasurementTimeStamp']
            measurementvalue = node['Measurementvalue']
            
            data_points = [measurementtimestamp, measurementvalue]
            nodeid = node['nodeid']

            print(nodeid)

            actual_data_points = {}

            for data in data_points:
                connector_id = data['connector']
                _logger.info("Getting info on data source:  %r", connector_id)
                response = dt_api.get('datasource/'+ connector_id)

                if response.status_code == 200:
                    con = response.json()

                    try:
                        module_name = "app.connectors.{0}".format(con['connector'])
                        print(module_name)
                        module = importlib.import_module(module_name)

                        Connector = getattr(module, con['connector'])
                        
                        connector = Connector()

                        print(data['mapping'])
                        # print(connector)
                        status = connector.connect(data['mapping'], con['connection_profile'])
                        
                        if status:
                            _logger.info("Connection initialized using")

                            resp = connector.get_data(mapping=data['mapping'])
                            
                            if resp:
                                _logger.info("Raw data received")

                                print(resp[0][0])
                               
                                for val in resp:
                                    opc_variable = client.get_node(ua.NodeId(int(data['nodeid']), 2))
                                    # obj = await client.nodes.root.get_child(["0:Objects", "2:West Wing Building"])
                                    _logger.info("myvar is: %r", opc_variable)
                                    
                                    await opc_variable.write_value(float(resp[0][0]))

                                    val = await opc_variable.read_value()
                                    # print(val)
                            
                        else:
                            _logger.error("Connection Failed")



                    except Exception as e:
                        
                        _logger.error("Error During Connection %r", e)
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