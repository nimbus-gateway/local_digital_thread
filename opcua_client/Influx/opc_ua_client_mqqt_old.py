import asyncio
import logging
import os
from config.config import Config
from comms.coms import RestClient
import importlib
import traceback
from datetime import datetime, timedelta
import argparse


from asyncua import Client, ua



# LOCAL DIGITAL THREAD VARIABLES
config_instance = Config()
conf = config_instance.get_config()
opc_config = conf['opc']
api_config = conf['data_source_manager']
dt_api = RestClient("http://{0}:{1}/".format(api_config['host'], api_config['port']))
opc_server_url = opc_config['server_url']


_logger = logging.getLogger(__name__)


# Create the parser
parser = argparse.ArgumentParser(description="OPC UA Data Ingestion Client Script for DBs.")


# Add an argument
parser.add_argument('--opcua_reference_id', type=str, help="this is ")
parser.add_argument('--all', action='store_true', help="A boolean flag. If present, stores True, otherwise False.")

# Parse the arguments
args = parser.parse_args()

opcua_reference_id = args.opcua_reference_id
all = args.all
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


async def push_data_to_opcua(client, measurementvalue_nid, measurementtimestamp_nid, data_array):
    opc_value_variable = client.get_node(ua.NodeId(int(measurementvalue_nid), 2))
    opc_time_variable = client.get_node(ua.NodeId(int(measurementtimestamp_nid), 2))
    _logger.info("opc_value_nodeid is: %r", measurementvalue_nid)
    _logger.info("opc_timestamp_nodeid is: %r", measurementtimestamp_nid)
    _logger.info("opc_value_variable is: %r", opc_value_variable)
    _logger.info("opc_time_variable is: %r", opc_time_variable)

    for val in data_array:
        print("setting value: {0} time stamp: {1}".format(str(val[1]), str(val[0])))
        data_value = ua.DataValue(ua.Variant(float(val[1]), ua.VariantType.Double), SourceTimestamp = datetime.utcfromtimestamp(val[0])) 

        # await opc_value_variable.write_value(float(val[1]))
        await opc_value_variable.write_value(data_value)

        await opc_time_variable.write_value(datetime.utcfromtimestamp(val[0]))

        val = await opc_value_variable.read_value()
        date = await opc_time_variable.read_value()

# Process MQTT messages and write to OPC UA
async def process_mqtt_to_opc(client, mqtt_buffer):
    while True:
        # Wait for MQTT message from the buffer
        mqtt_data = await mqtt_buffer.get()
        _logger.info("Retrieved Data From MQQT Buffer" + str(mqtt_data))

        # Write MQTT message to OPC UA server
        # await opc_write(opc_client, mqtt_data)
        print(mqtt_buffer)

async def main():
    url = opc_server_url

    # Connect to the OPC UA server
    async with Client(url=url) as client:
        _logger.info("Connected to OPC UA server at %s", url)
        _logger.info("Root node: %r", client.nodes.root)
        _logger.info("Objects node: %r", client.nodes.objects)


        # Retrieve and log the children of the root node
        root_children = await client.nodes.root.get_children()
        _logger.info("Children of root node: %r", root_children)

        # Get the namespace index for a specific URI
        uri = "http://examples.freeopcua.github.io"
        idx = await client.get_namespace_index(uri)
        _logger.info("Namespace index for %s: %s", uri, idx)

        # Retrieve nodes from an external API (Data Transformation API)
        response = dt_api.get('nodes')

        if response.status_code == 200:
                nodes = response.json()
                _logger.info("Received nodes from Data Transformation API: %r", nodes)
        else:
            _logger.error("Failed to retrieve nodes, status code: %r", response.status_code)
            return  # Exit the function if API call fails


        # Process each node returned by the API
        for node in nodes:
            if node['reference_id'] != opcua_reference_id:
                continue

            measurementtimestamp_nid = node['MeasurementTimeStamp']['nodeid']
            measurementvalue_nid = node['Measurementvalue']['nodeid']
            transformation = node["Transformation"]
            nodeid = node['nodeid']

            _logger.info("Processing node with ID: %r", nodeid)

            connector_id = transformation['connector']
            _logger.info("Fetching data source information for connector: %r", connector_id)

            # Get data source information
            response = dt_api.get(f'datasource/{connector_id}')

            if response.status_code == 200:
                con = response.json()

                try:
                    # Dynamically import and initialize the connector module
                    module_name = f"connectors.{con['connector']}"
                    _logger.info("Loading module: %s", module_name)
                    module = importlib.import_module(module_name)
                    Connector = getattr(module, con['connector'])
                    connector = Connector()

                    # Attempt to connect using the provided transformation and connection profile
                    _logger.info("Attempting to connect with data source")
                    status = connector.connect(transformation, con['connection_profile'])

                    buffer = connector.get_buffer()

                    if status:
                        _logger.info("Successfully connected with data source")

                        # Retrieve data from the data source
                        resp = connector.get_data(transformation=transformation)

                        if resp:
                            _logger.info("Raw data received: %r", resp)

                            # Push data to the OPC UA server
                            # push_data_to_opcua(client, measurementvalue_nid, measurementtimestamp_nid, resp)

                            print("waiting for the buffer")
                            await process_mqtt_to_opc(client, buffer)

                        else:
                            _logger.warning("No data received from data source")
                    else:
                        _logger.error("Failed to connect with data source")
                except Exception as e:
                    _logger.error("Error during connection setup: %r", e)
                    _logger.error(traceback.format_exc())
                    return  # Exit the function if there's an exception
            else:
                _logger.error("Connector Not registered :  %r", connector_id)
                continue

            
      
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # asyncio.run(main())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())