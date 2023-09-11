from opcua import Client

client = Client("opc.tcp://localhost:4840/freeopcua/server/")
client.connect()

# Retrieve a node by its object path
# my_var = client.get_node("ns=2;i=2")
# print("MyVariable value:", my_var.get_value())

machine1 = client.get_node("ns=2;i=2")
machine1_name = machine1.get_child(["2:Energy"]).set_value(54)

machine1_name = machine1.get_child(["2:Energy"]).get_value()

print("Value is:", machine1_name)


object_type_node = client.get_node("ns=2;i=2")

root = client.get_root_node()
new_instance = root.add_object(nodeid=None, browse_name="CommonEnergyMeter")

new_instance.get_child(["2:Energy"]).set_value(64)



class OpcClient():
    def __init__(self) -> None:
        self.client = Client("opc.tcp://localhost:4840/freeopcua/server/")
		
    def connect(self):
        self.client.connect()
	

    def disconnect(self):
        self.client.disconnect()

    def add_object(self):

        try:
            self.connect()

        except:
            return False

        self.disconnect()


# Write a value to the variable
# my_var.set_value(42)



