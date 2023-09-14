from opcua import Server, ua
from datetime import datetime
import os
from app.config.config import Config
from coms import RestClient


config_instance = Config("app/config/config.yaml")
opc_config = config_instance.get_opc_config()
api_config = config_instance.get_api_config()
api = RestClient("http://{0}:{1}/".format(api_config['host'], api_config['port']))



# Create a server instance
server = Server()

# Set server endpoint URL and port
url = opc_config['serverurl']
server.set_endpoint(url)

server.set_server_name(opc_config['servername'])

# Setup server namespace
uri = opc_config['namespaceuri']
idx = server.register_namespace(opc_config['namespace'])

# Create a new node for the namespace
root = server.nodes.objects.add_folder(idx, "MyInfoModel")

#methods to be exposed through server - to be implemented
def ConsumptionSummary(parent):
    print("Summary as follows")
    return 100

#define the object types
common_Weather_type = server.nodes.base_object_type.add_object_type(idx, "CommonWeather")
common_ElectricEnergyMeasurement_type = server.nodes.base_object_type.add_object_type(idx, "ElectricEnergyMeasurement")
common_Energy_type = server.nodes.base_object_type.add_object_type(idx, "CommonEnergy")
common_MeteringPoint_type = server.nodes.base_object_type.add_object_type(idx, "CommonMeteringPoint")
common_Machine_type = server.nodes.base_object_type.add_object_type(idx, "CommonMachine")
common_Building_type = server.nodes.base_object_type.add_object_type(idx, "CommonBuilding")
common_TimeSeriesMeasurement_type = server.nodes.base_object_type.add_object_type(idx, "TimeSeriesMeasurement")


#define the object TimeSeries Measurement
timestamp = common_TimeSeriesMeasurement_type.add_variable(idx, "TimeStamp", "XXXX", ua.VariantType.String)
value = common_TimeSeriesMeasurement_type.add_variable(idx, "Value", 0.0, ua.VariantType.Float)
timestamp.set_writable()
timestamp.set_modelling_rule(True) 
value.set_writable()
value.set_modelling_rule(True) 



#define the object weather
condition = common_Weather_type.add_variable(idx, "WeatherCondition", "", ua.VariantType.String).set_modelling_rule(True)
pressure = common_Weather_type.add_variable(idx, "AtmosphoricPressure", 0.0, ua.VariantType.Float).set_modelling_rule(True)
cloudage = common_Weather_type.add_variable(idx, "Cloudage", 0.0, ua.VariantType.Float).set_modelling_rule(True)
daytime = common_Weather_type.add_variable(idx, "DayTime", datetime.utcnow()).set_modelling_rule(True)
percipitation = common_Weather_type.add_variable(idx, "Precipitation", 0.0, ua.VariantType.Float).set_modelling_rule(True)
visibility = common_Weather_type.add_variable(idx, "Visibility", 0.0, ua.VariantType.Float).set_modelling_rule(True)

#define the object electric energy measurement
# timestamp_variable = common_ElectricEnergyMeasurement_type.add_variable(idx, "TimeStamp", "", ua.VariantType.String).set_modelling_rule(True)
# voltage_variable = common_ElectricEnergyMeasurement_type.add_variable(idx, "Voltage", 0.0, ua.VariantType.Float)
# current_variable = common_ElectricEnergyMeasurement_type.add_variable(idx, "Current", 0.0, ua.VariantType.Float).set_modelling_rule(True)
# power_variable = common_ElectricEnergyMeasurement_type.add_variable(idx, "Power", 0.0, ua.VariantType.Float).set_modelling_rule(True)
# common_ElectricEnergyMeasurement_type.add_object(idx, "Power", objecttype=common_TimeSeriesMeasurement_type).set_modelling_rule(True)



lock_variable = common_ElectricEnergyMeasurement_type.add_variable(idx, "Lock", 0.0, ua.VariantType.Int32).set_modelling_rule(True)
common_ElectricEnergyMeasurement_type.add_method(idx, "DailyConsumption", ConsumptionSummary, ["", "Return", "Float"], ["", "Input", "String"]).set_modelling_rule(True)
common_ElectricEnergyMeasurement_type.add_method(idx, "MonthlyConsumption", ConsumptionSummary, ["", "Return", "Float"], ["", "Input", "String"]).set_modelling_rule(True)

#define the object energy  
# thermal_variable = common_Energy_type.add_property(idx, "Thermal", "").set_modelling_rule(True)
# gas_variable = common_Energy_type.add_property(idx, "Gas", "").set_modelling_rule(True)
# common_Energy_type.add_object(idx, "Electric", objecttype=common_ElectricEnergyMeasurement_type).set_modelling_rule(True)

#define the object metering point
communication_protocol_variable = common_MeteringPoint_type.add_variable(idx, "CommunicationProtocol", "", ua.VariantType.String).set_modelling_rule(True)
sampling_rate_variable = common_MeteringPoint_type.add_variable(idx, "SamplingRate", 0.0, ua.VariantType.Float).set_modelling_rule(True)
# alerts_variable = common_MeteringPoint_type.add_variable(idx, "Alerts", "", ua.VariantType).set_modelling_rule(True)

#define the object machine
name_variable = common_Machine_type.add_property(idx, "Name", "", ua.VariantType.String).set_modelling_rule(True)
model_variable = common_Machine_type.add_property(idx, "Model", "", ua.VariantType.String).set_modelling_rule(True)
machine_type_variable = common_Machine_type.add_property(idx, "Type", "", ua.VariantType.String).set_modelling_rule(True)
machine_ID_variable = common_Machine_type.add_property(idx, "ID", "", ua.VariantType.Int32).set_modelling_rule(True)
manufacturer_variable = common_Machine_type.add_property(idx, "Manufacturer", "", ua.VariantType.String).set_modelling_rule(True)
status_variable = common_Machine_type.add_variable(idx, "Status", "", ua.VariantType.String).set_modelling_rule(True)
location_variable = common_Machine_type.add_property(idx, "BuildingName", "", ua.VariantType.String).set_modelling_rule(True)

#define the object building
location_variable = common_Building_type.add_property(idx, "Coordinates", "", ua.VariantType.String).set_modelling_rule(True)
area_variable = common_Building_type.add_property(idx, "Area", "", ua.VariantType.Float).set_modelling_rule(True)
address_variable = common_Building_type.add_property(idx, "Address", "", ua.VariantType.String).set_modelling_rule(True)



machine_data_objects = {}
metering_points_data_objects = {}
energy_type_objects = {}
energy_types = ["Electric", "Gas", "Thermal"]

energy_variable_objects = {}
energy_variables = ["Current", "Power", "Voltage"]


cwd = os.path.abspath('./')

response = api.get('getMapping')

if response.status_code == 200:
    mapping = response.json()
    print("Response from API: ", mapping)
else:
    exit()

# Mapping(cwd + '/rest/mapping/mapping.json')

#function to add energy measurement types to the energy type object
def add_energy_type_to_energy_folder(energy_type, folder, enery_objects):
    energy_type_objects[energy_type] = folder.add_object(idx, f"{energy_type}", objecttype=common_ElectricEnergyMeasurement_type)

    

    power_object = energy_type_objects[energy_type].add_object(idx, "Power", objecttype=common_TimeSeriesMeasurement_type)
    voltage_object = energy_type_objects[energy_type].add_object(idx, "Voltage", objecttype=common_TimeSeriesMeasurement_type)
    current_object = energy_type_objects[energy_type].add_object(idx, "Current", objecttype=common_TimeSeriesMeasurement_type)

   
    if "Mapping" in enery_objects[energy_type]["Power"]:
        input = {'nodeid': power_object.nodeid.Identifier, 'mapping': enery_objects[energy_type]["Power"]["Mapping"]}
        api.post('registerNode', input)
        # mapping.register_nodeid(power_object.nodeid.Identifier, enery_objects[energy_type]["Power"]["Mapping"])

    elif "Mapping" in enery_objects[energy_type]["Voltage"]:
        input = {'nodeid': voltage_object.nodeid.Identifier, 'mapping': enery_objects[energy_type]["Voltage"]["Mapping"]}
        api.post('registerNode', input)
        # mapping.register_nodeid(voltage_object.nodeid.Identifier, enery_objects[energy_type]["Voltage"]["Mapping"])

    elif "Mapping" in enery_objects[energy_type]["Current"]:
        input = {'nodeid': current_object.nodeid.Identifier, 'mapping': enery_objects[energy_type]["Current"]["Mapping"]}
        api.post('registerNode', input)
        # mapping.register_nodeid(current_object.nodeid.Identifier, enery_objects[energy_type]["Current"]["Mapping"])

    
   

#function to add metering points to the machine objects
def add_metering_point_objects_to_machine_folder(metering_point, folder):
    metering_points_data_objects[metering_point['MateringPointName']] = folder.add_object(idx, f"{metering_point['MateringPointName']}", objecttype=common_MeteringPoint_type)
    energy_folder = metering_points_data_objects[metering_point['MateringPointName']].add_folder(idx, "EnergyTypes")

    print(metering_point)
    for energy_type in energy_types:
        add_energy_type_to_energy_folder(energy_type,energy_folder, metering_point['EnergyObject'])

#function to add machines to the machine folder
def add_machine_objects_to_building(machine_name, folder, metering_points):
    machine_data_objects[machine_name] = folder.add_object(idx, f"{machine_name}", objecttype=common_Machine_type)
    MP_folder = machine_data_objects[machine_name].add_folder(idx, "MeteringPoints")
    for metering_point in metering_points:
        add_metering_point_objects_to_machine_folder(metering_point, MP_folder)




buildings = mapping['Buildings']



for Building in buildings:

    building = root.add_object(idx, Building['BuildingName'], objecttype=common_Building_type)
    building.add_object(idx, "Weather", objecttype=common_Weather_type)
    machine_folder = building.add_folder(idx, "Machines")


    for machine in Building['Machines']:
        add_machine_objects_to_building(machine['Name'], machine_folder, machine['MeteringPoints'])

    


     #     energy_meter_a.get_child(["2:TimeStamp"]).set_value(dt)






server.start()

try:
    while True:
        pass  # Keep the server running
except KeyboardInterrupt:
    server.stop()



