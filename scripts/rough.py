from opcua import Client

def browse_recursive(node, indent=0):
    print("  " * indent + f"{node.get_display_name().Text} (NodeID: {node.nodeid})")
    children = node.get_children()
    for child in children:
        browse_recursive(child, indent + 1)

def main():
    # Connect to the OPC UA server
    url = "opc.tcp://0.0.0.0:4840/freeopcua/server/"  # Replace with the server's endpoint URL
    client = Client(url)
    try:
        client.connect()
        print("Connected to OPC UA server.")

        # Get the root node
        root = client.get_root_node()

        # Browse the server's address space recursively
        print("Browsing the server's address space:")
        browse_recursive(root)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Disconnect from the server
        client.disconnect()
        print("Disconnected from OPC UA server.")

if __name__ == "__main__":
    main()
