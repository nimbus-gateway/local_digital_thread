from opcua import Client

url = "opc.tcp://localhost:4840/freeopcua/server/"

# Create a client and connect to the server
client = Client(url)
client.connect()

# Access the objects and variables from the server

# Machine 1
machine1 = client.get_node("ns=2;i=1")
machine1_name = machine1.get_child(["2:Name"]).get_value()
machine1_id = machine1.get_child(["2:ID"]).get_value()
machine1_location = machine1.get_child(["2:Location"]).get_value()
machine1_manufacturer = machine1.get_child(["2:Manufacturer"]).get_value()
machine1_model = machine1.get_child(["2:Model"]).get_value()
machine1_status = machine1.get_child(["2:Status"]).get_value()

machine1_consumption = machine1.get_child(["2:EnergyConsumption"])
machine1_total_energy_consumption = machine1_consumption.get_child(["2:TotalEnergyConsumption"]).get_value()
machine1_daily_energy_consumption = machine1_consumption.get_child(["2:DailyEnergyConsumption"]).get_value()
machine1_monthly_energy_consumption = machine1_consumption.get_child(["2:MonthlyEnergyConsumption"]).get_value()
machine1_annual_energy_consumption = machine1_consumption.get_child(["2:AnnualEnergyConsumption"]).get_value()

machine1_production = machine1.get_child(["2:EnergyProduction"])
machine1_total_energy_production = machine1_production.get_child(["2:TotalEnergyProduction"]).get_value()
machine1_daily_energy_production = machine1_production.get_child(["2:DailyEnergyProduction"]).get_value()
machine1_monthly_energy_production = machine1_production.get_child(["2:MonthlyEnergyProduction"]).get_value()
machine1_annual_energy_production = machine1_production.get_child(["2:AnnualEnergyProduction"]).get_value()

# Machine 2
machine2 = client.get_node("ns=2;i=2")
machine2_name = machine2.get_child(["2:Name"]).get_value()
machine2_id = machine2.get_child(["2:ID"]).get_value()
machine2_location = machine2.get_child(["2:Location"]).get_value()
machine2_manufacturer = machine2.get_child(["2:Manufacturer"]).get_value()
machine2_model = machine2.get_child(["2:Model"]).get_value()
machine2_status = machine2.get_child(["2:Status"]).get_value()

machine2_consumption = machine2.get_child(["2:EnergyConsumption"])
machine2_total_energy_consumption = machine2_consumption.get_child(["2:TotalEnergyConsumption"]).get_value()
machine2_daily_energy_consumption = machine2_consumption.get_child(["2:DailyEnergyConsumption"]).get_value()
machine2_monthly_energy_consumption = machine2_consumption.get_child(["2:MonthlyEnergyConsumption"]).get_value()
machine2_annual_energy_consumption = machine2_consumption.get_child(["2:AnnualEnergyConsumption"]).get_value()

machine2_production = machine2.get_child(["2:EnergyProduction"])
machine2_total_energy_production = machine2_production.get_child(["2:TotalEnergyProduction"]).get_value()
machine2_daily_energy_production = machine2_production.get_child(["2:DailyEnergyProduction"]).get_value()
machine2_monthly_energy_production = machine2_production.get_child(["2:MonthlyEnergyProduction"]).get_value()
machine2_annual_energy_production = machine2_production.get_child(["2:AnnualEnergyProduction"]).get_value()

# Display the information
print("Machine 1:")
print("Name:", machine1_name)
print("ID:", machine1_id)
print("Location:", machine1_location)
print("Manufacturer:", machine1_manufacturer)
print("Model:", machine1_model)
print("Status:", machine1_status)
print("Total Energy Consumption:", machine1_total_energy_consumption)
print("Daily Energy Consumption:", machine1_daily_energy_consumption)
print("Monthly Energy Consumption:", machine1_monthly_energy_consumption)
print("Annual Energy Consumption:", machine1_annual_energy_consumption)
print("Total Energy Production:", machine1_total_energy_production)
print("Daily Energy Production:", machine1_daily_energy_production)
print("Monthly Energy Production:", machine1_monthly_energy_production)
print("Annual Energy Production:", machine1_annual_energy_production)

print("\nMachine 2:")
print("Name:", machine2_name)
print("ID:", machine2_id)
print("Location:", machine2_location)
print("Manufacturer:", machine2_manufacturer)
print("Model:", machine2_model)
print("Status:", machine2_status)
print("Total Energy Consumption:", machine2_total_energy_consumption)
print("Daily Energy Consumption:", machine2_daily_energy_consumption)
print("Monthly Energy Consumption:", machine2_monthly_energy_consumption)
print("Annual Energy Consumption:", machine2_annual_energy_consumption)
print("Total Energy Production:", machine2_total_energy_production)
print("Daily Energy Production:", machine2_daily_energy_production)
print("Monthly Energy Production:", machine2_monthly_energy_production)
print("Annual Energy Production:", machine2_annual_energy_production)

# Disconnect the client
client.disconnect()
