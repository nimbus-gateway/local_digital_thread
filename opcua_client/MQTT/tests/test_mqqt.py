import paho.mqtt.client as mqtt

# Define the MQTT broker details
MQTT_BROKER = "192.168.76.25"  # Replace with your MQTT broker IP or URL
MQTT_PORT = 1883  # Standard MQTT port (1883) or other if needed

# The callback for when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_BROKER} on port {MQTT_PORT} - Status: SUCCESS")
        # Subscribe to all topics
        client.subscribe("#")
        print("Subscribed to all topics")
    else:
        print(f"Failed to connect to MQTT broker - Status: {rc}")

# The callback for when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} | Message: {msg.payload.decode()}")

# Create a new MQTT client instance
client = mqtt.Client()

# Attach callback functions
client.on_connect = on_connect
client.on_message = on_message

try:
    # Connect to the broker
    print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Start the loop
    client.loop_forever()

except Exception as e:
    print(f"Error: {e}")

finally:
    # Disconnect the client
    client.disconnect()
