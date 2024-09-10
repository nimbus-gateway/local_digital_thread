import asyncio
import logging
import os
from config.config import Config
from comms.coms import RestClient
import importlib
import traceback
from datetime import datetime, timedelta
import argparse
import json

from influxdb_client import InfluxDBClient
from asyncua import Client, ua


# LOCAL DIGITAL THREAD VARIABLES
config_instance = Config()
conf = config_instance.get_config()
opc_config = conf['opc']
api_config = conf['data_source_manager']
dt_api = RestClient("http://{0}:{1}/".format(api_config['host'], api_config['port']))
opc_server_url = opc_config['server_url']
reference_id = opc_config['reference_id']
# Buffer to hold incoming InfluxDB messages
influxdb_buffer = asyncio.Queue()
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
    unix_epoch = datetime(1970, 1, 1)
    ua_epoch = datetime(1601, 1, 1)
    delta_to_unix_epoch = unix_epoch - ua_epoch
    total_seconds = delta_to_unix_epoch.total_seconds() + unix_timestamp
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

    # FIX THIS ISSUE: Incomptible Format
    # await opc_time_variable.write_value(time_data)


async def safe_put(queue, data):
    try:
        queue.put_nowait(data)
    except asyncio.QueueFull:
        await queue.get()
        await queue.put(data)


async def query_influxdb(client, opc_client, org, query, measurementvalue_nid, measurementtimestamp_nid):
    """
    Periodically query InfluxDB and process new data to push to OPC UA server.
    """
    while True:
        # Query the InfluxDB client
        result = client.query_api().query(query=query, org=org)
        
        for table in result:
            for record in table.records:
                value_data = record.get_value()
                time_data = record.get_time().timestamp()  # Convert to Unix timestamp
                print("value_data = " + str(value_data))

                await push_data_to_opcua(opc_client, measurementvalue_nid, measurementtimestamp_nid, value_data, time_data)

        await asyncio.sleep(5)  # Wait for 2 seconds before next query


async def main():
    url = opc_server_url
    global loop
    loop = asyncio.get_running_loop()  # Get the current asyncio loop


    # Connect to the OPC UA server
    async with Client(url=url) as opc_client:
        _logger.info("Connected to OPC UA server at %s", url)
        _logger.info("Root node: %r", opc_client.nodes.root)
        _logger.info("Objects node: %r", opc_client.nodes.objects)


        # Retrieve and log the children of the root node
        root_children = await opc_client.nodes.root.get_children()
        _logger.info("Children of root node: %r", root_children)

        # Get the namespace index for a specific URI
        uri = "http://examples.freeopcua.github.io"
        idx = await opc_client.get_namespace_index(uri)
        _logger.info("Namespace index for %s: %s", uri, idx)

        # Retrieve nodes from an external API (Data Transformation API)
        response = dt_api.get('nodes')
        if response.status_code == 200:
            nodes = response.json()
            _logger.info("Received nodes from Data Transformation API: %r", nodes)
        else:
            _logger.error("Failed to retrieve nodes, status code: %r", response.status_code)
            return  # Exit the function if API call fails

        _logger.info("Start pushing data into OPCUA reference id: %r", opcua_reference_id)
        
        # Process each node returned by the API
        for node in nodes:
            print(node)
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
                    _logger.info("Setting up InfluxDB Client")
                    _logger.info("Data source metadata: %r", con)
                    host = con['connection_profile']['host']
                    port = con['connection_profile']['port']
                    token = con['connection_profile']['token']
                    org = con['connection_profile']['org']
                    bucket = transformation['dbname']
                    query = transformation['query']  # InfluxDB query to fetch the desired data
                    mapping = transformation['mapping']
                    fieled_name = transformation['mapping']['Measurementvalue'] 
                    measurement = transformation['table']

                    query = """from(bucket: "{0}")
                            |> range(start: -2m)
                            |> filter(fn: (r) => r["_field"] == "{1}")
                            |> filter(fn: (r) => r._measurement == "{2}")""".format(bucket, fieled_name, measurement)

                    influxdb_url = url = "http://{0}:{1}".format(host, port)
                    influx_client = InfluxDBClient(url=influxdb_url, token=token, org=org)
                    _logger.info("Influx connection success")

                    # Query InfluxDB and push data to OPC UA
                    await query_influxdb(influx_client, opc_client, org, query, measurementvalue_nid, measurementtimestamp_nid)

                except Exception as e:
                    _logger.error("InfluxDB related Error Occurred: %r", e)
                    _logger.error(traceback.format_exc())
                    return
            else:
                _logger.error("Connector Not registered :  %r", connector_id)
                continue


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
