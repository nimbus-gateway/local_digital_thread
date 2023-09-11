from opcua import Server, ua

i=0
# Create a server instance
server = Server()

# Set server endpoint URL and port
url = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
server.set_endpoint(url)

server.set_server_name("Energy Model Server-Sample")

# Setup server namespace
uri = "http://example.org"
idx = server.register_namespace(uri)

# Create a new node for the namespace
root = server.nodes.objects.add_object(idx, "MyServer")

# Define an object for representing a machine
machine_type = server.nodes.base_object_type.add_object_type(idx, "MachineType")
machine_type.add_variable(idx, "Name", "").set_modelling_rule(True)
machine_type.add_variable(idx, "ID", 0).set_modelling_rule(True)
machine_type.add_variable(idx, "Location", "").set_modelling_rule(True)
machine_type.add_variable(idx, "Manufacturer", "").set_modelling_rule(True)
machine_type.add_variable(idx, "Model", "").set_modelling_rule(True)
machine_type.add_variable(idx, "Status", False).set_modelling_rule(True)



#Define an object for representing the energy consumption
energy_consumption_type = server.nodes.base_object_type.add_object_type(idx, "EnergyConsumptionType")
energy_consumption_type.add_variable(idx, "TotalEnergyConsumption", 0.0).set_modelling_rule(True)
my_daily_consumption = energy_consumption_type.add_variable(idx, "DailyEnergyConsumption", 0.0).set_modelling_rule(True)
energy_consumption_type.add_variable(idx, "MonthlyEnergyConsumption", 0.0).set_modelling_rule(True)
energy_consumption_type.add_variable(idx, "AnnualEnergyConsumption", 0.0).set_modelling_rule(True)

machine1 = root.add_object(idx, "Machine1", objecttype=machine_type)
#machine1.set_display_name("Machine 1")

#machine1.set_attribute(ua.AttributeIds.DisplayName, ua.LocalizedText("en", "Machine 1"))
machine2 = root.add_object(idx, "Machine2", objecttype=machine_type)
#machine2.set_display_name("Machine 2")
#machine2.set_attribute(ua.AttributeIds.DisplayName, ua.LocalizedText("en", "Machine 2"))

# Add energy consumption and production data objects for each machine
machine1_consumption = machine1.add_object(idx, "EnergyConsumption", objecttype=energy_consumption_type)
machine2_consumption = machine2.add_object(idx, "EnergyConsumption", objecttype=energy_consumption_type)

# Set the custom variables writable

for obj in [machine1_consumption, machine2_consumption]:
    for child in obj.get_children():
        child.set_writable()

#export the model to xml file
server.export_xml_by_ns('Energy_Server_Model.xml',namespaces="Energy Model Server")

# Start the server
server.start()

try:
    while True:
        # Update the custom variables' values periodically (you can use real data here)
        machine1.get_child(["2:Name"]).set_value("Machine 1")
        machine1.get_child(["2:ID"]).set_value(1)
        machine1.get_child(["2:Location"]).set_value("Facility A")
        machine1.get_child(["2:Manufacturer"]).set_value("Manufacturer X")
        machine1.get_child(["2:Model"]).set_value("Model 123")
        machine1.get_child(["2:Status"]).set_value(True)

        machine1_consumption.get_child(["2:TotalEnergyConsumption"]).set_value(1000.0)
        machine1_consumption.get_child(["2:DailyEnergyConsumption"]).set_value(i*2.0)
        machine1_consumption.get_child(["2:MonthlyEnergyConsumption"]).set_value(1000.0)
        machine1_consumption.get_child(["2:AnnualEnergyConsumption"]).set_value(12000.0)

        machine2.get_child(["2:Name"]).set_value("Machine 2")
        machine2.get_child(["2:ID"]).set_value(2)
        machine2.get_child(["2:Location"]).set_value("Facility B")
        machine2.get_child(["2:Manufacturer"]).set_value("Manufacturer Y")
        machine2.get_child(["2:Model"]).set_value("Model 456")
        machine2.get_child(["2:Status"]).set_value(False)

        machine2_consumption.get_child(["2:TotalEnergyConsumption"]).set_value(1200.0)
        machine2_consumption.get_child(["2:DailyEnergyConsumption"]).set_value(60.0)
        machine2_consumption.get_child(["2:MonthlyEnergyConsumption"]).set_value(1200.0)
        machine2_consumption.get_child(["2:AnnualEnergyConsumption"]).set_value(14400.0)
        i=i+1
        # Sleep for a short interval before the next update
        import time
        time.sleep(5)

except KeyboardInterrupt:
    # Stop the server gracefully when Ctrl+C is pressed
    server.stop()