from opcua import Client

# Connect to the server
client = Client("opc.tcp://localhost:4840/freeopcua/server/")
client.connect()

try:
    # Get the root node
    root = client.get_root_node()

    # Get the ManufacturingEnergy object
    manufacturing_energy_obj = root.get_child(["0:Objects", "2:ManufacturingEnergy"])

    # Read the Power variable
    power_variable = manufacturing_energy_obj.get_child(["2:Power"])
    power_value = power_variable.get_value()
    print("Power Value:", power_value)

    # Call the StartProduction method
    start_production_method = manufacturing_energy_obj.get_child(["2:StartProduction"])
    result = start_production_method.call_method(100.0)  # Pass energy value as an argument
    print("Start Production Result:", result)

finally:
    client.disconnect()
