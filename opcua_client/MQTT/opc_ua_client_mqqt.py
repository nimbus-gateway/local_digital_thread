import asyncio
import logging
import os
from config.config import Config
from comms.coms import RestClient
import importlib
import traceback
from datetime import datetime, timedelta
import argparse
import paho.mqtt.client as mqtt
import json


from asyncua import Client, ua



# LOCAL DIGITAL THREAD VARIABLES
config_instance = Config()
conf = config_instance.get_config()
opc_config = conf['opc']
api_config = conf['data_source_manager']
dt_api = RestClient("http://{0}:{1}/".format(api_config['host'], api_config['port']))
opc_server_url = opc_config['server_url']
reference_id = opc_config['reference_id']
# Buffer to hold incoming MQTT messages
mqtt_buffer = asyncio.Queue()
# Main event loop reference
loop = None

print(reference_id)

_logger = logging.getLogger(__name__)


# Create the parser
parser = argparse.ArgumentParser(description="OPC UA Data Ingestion Client Script for DBs.")


# Add an argument
parser.add_argument('--opcua_reference_id', type=str, default=reference_id, help="reference  if node")

# Parse the arguments
args = parser.parse_args()

opcua_reference_id = args.opcua_reference_id


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


async def push_data_to_opcua(client, measurementvalue_nid, measurementtimestamp_nid, value_data, time_data):
    opc_value_variable = client.get_node(ua.NodeId(int(measurementvalue_nid), 2))
    opc_time_variable = client.get_node(ua.NodeId(int(measurementtimestamp_nid), 2))
    _logger.info("opc_value_nodeid is: %r", measurementvalue_nid)
    _logger.info("opc_timestamp_nodeid is: %r", measurementtimestamp_nid)
    _logger.info("opc_value_variable is: %r", opc_value_variable)
    _logger.info("opc_time_variable is: %r", opc_time_variable)

    _logger.info("pushing data to opcua server ")
    await opc_value_variable.write_value(float(value_data))

    # await opc_time_variable.write_value(time_data)


    # for val in data_array:
    #     print("setting value: {0} time stamp: {1}".format(str(val[1]), str(val[0])))
    #     data_value = ua.DataValue(ua.Variant(float(val[1]), ua.VariantType.Double), SourceTimestamp = datetime.utcfromtimestamp(val[0])) 

    #     # await opc_value_variable.write_value(float(val[1]))
    #     await opc_value_variable.write_value(data_value)

    #     await opc_time_variable.write_value(datetime.utcfromtimestamp(val[0]))

    #     val = await opc_value_variable.read_value()
    #     date = await opc_time_variable.read_value()


# Make sure that queue dont overflow
async def safe_put(queue, data):
    try:
        queue.put_nowait(data)  # Try to put data without blocking
    except asyncio.QueueFull:
        # Remove oldest message to make room for new data
        await queue.get()
        await queue.put(data)


# MQTT on_message callback
def on_message(client, userdata, message):
    global loop

    # Decode the incoming MQTT message
    mqtt_data = message.payload.decode("utf-8")
    # print(f"Received MQTT message: {mqtt_data}")

    # Use run_coroutine_threadsafe to put data into the async queue
    if loop:
        future = asyncio.run_coroutine_threadsafe(safe_put(mqtt_buffer, mqtt_data), loop)
        future.result()  # Optional: wait for the result




# MQTT setup
def mqtt_setup(host, port, topic, username, password):
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    _logger.info("Initializing the connection with MQTT Broker host: %s, port: %s", host, str(port))

    mqtt_client.connect(host, port)

    if username and password:
        mqtt_client.username_pw_set(username, password)

    _logger.info("Subscribing the topic: %s", topic)
    mqtt_client.subscribe(topic)
    mqtt_client.loop_start()  # Start MQTT listening in a separate thread
    return mqtt_client


# Process MQTT messages and write to OPC UA
async def process_mqtt_to_opc(client, measurementvalue_nid, measurementtimestamp_nid, mapping):
    while True:
        # Wait for MQTT message from the buffer
        mqtt_data = await mqtt_buffer.get()
        _logger.info("Retrieved Data From MQTT Buffer" + str(mqtt_data))

        try:
            message_dict = json.loads(mqtt_data)
            value_data = message_dict[mapping['Measurementvalue']]
            time_val = message_dict[mapping['MeasurementTimeStamp']]
            date_time_obj = datetime.strptime(time_val, "%Y-%m-%d %H:%M:%S")
            unix_timestamp = int(date_time_obj.timestamp())
            time_data = unix_timestamp

        except Exception as e:
            _logger.error("Cant transform MQTT Data: %r", e)
            _logger.error(traceback.format_exc())
            return 

        # Write MQTT message to OPC UA server
        # await opc_write(opc_client, mqtt_data)
        await push_data_to_opcua(client, measurementvalue_nid, measurementtimestamp_nid, value_data, time_data)
        # await asyncio.sleep(1)

async def main():
    url = opc_server_url
    global loop
    loop = asyncio.get_running_loop()  # Get the current asyncio loop

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


        _logger.error("Start pushing data into OPCUA reference id: %r", opcua_reference_id)
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
                    # module_name = f"connectors.{con['connector']}"
                    # _logger.info("Loading module: %s", module_name)
                    # module = importlib.import_module(module_name)
                    # Connector = getattr(module, con['connector'])

                    _logger.info("Setting up the MQQT Client")
                    host = con['connection_profile']['host']
                    port = int(con['connection_profile']['port'])
                    username = con['connection_profile']['username']
                    password = con['connection_profile']['password']
                    topic = transformation['topic']
                    mapping = transformation['mapping']
                    mqtt_setup(host, port, topic, username, password)


                    # Run the process that handles MQTT to OPC UA writes
                    await process_mqtt_to_opc(client, measurementvalue_nid, measurementtimestamp_nid, mapping)


                except Exception as e:
                    _logger.error("MQQT related Error Occured: %r", e)
                    _logger.error(traceback.format_exc())
                    return  # Exit the function if there's an exception
            else:
                _logger.error("Connector Not registered :  %r", connector_id)
                continue

            
      

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # asyncio.run(main())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())