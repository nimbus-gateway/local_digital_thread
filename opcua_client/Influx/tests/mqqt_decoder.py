import paho.mqtt.client as mqtt

def subscribe_and_decode(broker_address, topic, username=None, password=None):
    """
    Subscribes to an MQTT topic and decodes the received data.

    :param broker_address: The address of the MQTT broker.
    :param topic: The topic to subscribe to.
    :param username: Optional username for MQTT broker authentication.
    :param password: Optional password for MQTT broker authentication.
    """
    
    def on_connect(client, userdata, flags, rc):
        """
        Callback function when the client connects to the broker.
        """
        if rc == 0:
            print(f"Connected to MQTT broker at {broker_address}")
            client.subscribe(topic)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(client, userdata, message):
        """
        Callback function when a message is received on the subscribed topic.
        Decodes and processes the message payload.
        """
        try:
            decoded_message = message.payload.decode("utf-8")
            print(f"Received message '{decoded_message}' on topic '{message.topic}'")
            # Process the message here if needed (e.g., parse JSON, etc.)
        except Exception as e:
            print(f"Failed to decode message: {e}")

    # Create an MQTT client instance
    client = mqtt.Client()

    # Set up the username and password if provided
    if username and password:
        client.username_pw_set(username, password)

    # Assign the callback functions
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(broker_address)

    # Start the MQTT client loop to process messages
    client.loop_forever()

# Example usage
subscribe_and_decode("127.0.0.1", "sensor/opied1/synthetic_data")

