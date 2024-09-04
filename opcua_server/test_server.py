import sys
from opcua import Client
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def main(opcua_url):
    try:
        # Create an OPC UA client instance
        client = Client(opcua_url)
        
        # Connect to the server
        client.connect()
        _logger.info(f"Connected to OPC UA Server at {opcua_url}")
        
        # Get the root node
        root = client.get_root_node()
        _logger.info(f"Root node is: {root}")
        
        # Get the children of the root node
        children = root.get_children()
        _logger.info(f"Children of root node are: {children}")

        # Optionally, print some child nodes' names
        for child in children:
            _logger.info(f"Child node: {child}, Display name: {child.get_display_name().Text}")

    except Exception as e:
        _logger.error(f"Failed to connect to OPC UA Server: {e}")
    finally:
        # Ensure that the client disconnects even if there is an error
        client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        _logger.error("Usage: python opcua_client.py <opcua_server_url>")
        sys.exit(1)

    opcua_url = sys.argv[1]
    main(opcua_url)
