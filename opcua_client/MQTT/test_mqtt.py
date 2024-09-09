import asyncio
import paho.mqtt.client as mqtt
from asyncua import Client

# MQTT Settings
MQTT_BROKER = "127.0.0.1"
MQTT_TOPIC = "sensor/opied1/synthetic_data"

# OPC UA Settings
OPC_SERVER_URL = "opc.tcp://localhost:4840/freeopcua/server/"
OPC_NODE_ID = "ns=2;i=2"  # Example node id to write to

# Buffer to hold incoming MQTT messages
mqtt_buffer = asyncio.Queue()

# Main event loop reference
loop = None

# MQTT on_message callback
def on_message(client, userdata, message):
    global loop

    # Decode the incoming MQTT message
    mqtt_data = message.payload.decode("utf-8")
    # print(f"Received MQTT message: {mqtt_data}")

    # Use run_coroutine_threadsafe to put data into the async queue
    if loop:
        future = asyncio.run_coroutine_threadsafe(mqtt_buffer.put(mqtt_data), loop)
        future.result()  # Optional: wait for the result

# MQTT setup
def mqtt_setup():
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER)

    mqtt_client.subscribe(MQTT_TOPIC)
    mqtt_client.loop_start()  # Start MQTT listening in a separate thread
    return mqtt_client

# OPC UA write function
async def opc_write(opc_client, value):
    try:
        node = opc_client.get_node(OPC_NODE_ID)
        await node.write_value(value)
        print(f"OPC UA value written: {value}")
    except Exception as e:
        print(f"Error writing to OPC UA: {e}")

# Process MQTT messages and write to OPC UA
async def process_mqtt_to_opc():
    async with Client(OPC_SERVER_URL) as opc_client:
        while True:
            # Wait for MQTT message from the buffer
            mqtt_data = await mqtt_buffer.get()


            print("Recieved Data From MQQT")
            print(mqtt_data)
            # Write MQTT message to OPC UA server
            # await opc_write(opc_client, mqtt_data)

# Main asynchronous event loop
async def main():
    global loop
    loop = asyncio.get_running_loop()  # Get the current asyncio loop

    # Setup MQTT connection and start subscribing
    mqtt_setup()

    # Run the process that handles MQTT to OPC UA writes
    await process_mqtt_to_opc()

# Start the event loop
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
