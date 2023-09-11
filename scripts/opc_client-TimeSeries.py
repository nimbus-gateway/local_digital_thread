from opcua import Client, ua

client = Client("opc.tcp://localhost:4840/freeopcua/server/")
client.connect()

# Get the root node
root = client.get_root_node()


# Define a NodeId for the new object instance (you can adjust the namespace and identifier)
object_id = ua.NodeId("2:CommonEnergyMeter", 2)  # Namespace index is 2


print(object_id)

energy_meter_a = root.add_object(nodeid=object_id, bname="meterc", )


# machine1 = client.get_node("ns=2;i=2")
# machine1_name = machine1.get_child(["2:Energy"]).set_value(54)

# machine1_name = machine1.get_child(["2:Energy"]).get_value()

# print("Value is:", machine1_name)


# object_type_node = client.get_node("ns=2;i=2")

# root = client.get_root_node()
# new_instance = root.add_object(nodeid=None, browse_name="CommonEnergyMeter")

# new_instance.get_child(["2:Energy"]).set_value(64)





# Write a value to the variable
# my_var.set_value(42)

client.disconnect()

