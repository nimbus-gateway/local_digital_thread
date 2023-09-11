from opcua import Client

def get_object_type_node_id(client, object_type_name):
    root = client.get_root_node()
    
    try:
        object_type_node = root.get_child(["0:Types", f"2:{object_type_name}"])
        return object_type_node.nodeid
    except Exception as e:
        print(f"Error: {e}")
        return None

client = Client("opc.tcp://localhost:4840/freeopcua/server/")
client.connect()

object_type_name = "CommonEnergyMeter"  # Replace with the actual ObjectType name
object_type_node_id = get_object_type_node_id(client, object_type_name)

if object_type_node_id:
    print(f"NodeId of {object_type_name} ObjectType:", object_type_node_id)

client.disconnect()