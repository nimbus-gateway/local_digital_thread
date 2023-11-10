from opcua import Server, ua
from opcua.common.xmlexporter import XmlExporter
import mysql
from mysql import connector
from datetime import datetime
import time

# Create a server instance
server = Server()

# Set server endpoint URL and port
url = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
server.set_endpoint(url)

server.set_server_name("InfoModel_Server")

# Setup server namespace
uri = "http://example.org"
idx = server.register_namespace("OPCUA_SERVER")

# Create a new node for the namespace
root = server.nodes.objects.add_folder(idx, "MyInfoModel")

#methods to be exposed through server - to be implemented
def dailyAverage(parent, inputs, outputs):
    print("Summary as follows")
    return []

def monthlyAverage(parent, inputs, outputs):
    print("Summary as follows")
    return []

# method for turning the device on
def turn_on(parent, inputs, outputs):
    state_variable.set_value("On")
    return []

#method for turning the device off
def turn_off(parent, inputs, outputs):
    state_variable.set_value("Off")
    return []

#define the object types
common_Weather_type = server.nodes.base_object_type.add_object_type(idx, "CommonWeather")
common_Device_type = server.nodes.base_object_type.add_object_type(idx, "CommonDevice")
common_Building_type = server.nodes.base_object_type.add_object_type(idx, "CommonBuilding")
common_Location_type = server.nodes.base_object_type.add_object_type(idx, "CommonLocation")
common_Measurement_type = server.nodes.base_object_type.add_object_type(idx, "CommonMeasurementType")
common_MeteringProperty_type = server.nodes.base_object_type.add_object_type(idx, "CommonMeteringPropertyType")
common_Service_type = server.nodes.base_object_type.add_object_type(idx, "CommonService")

#define the object location
latitude = common_Location_type.add_variable(idx, "Latitude", "", ua.VariantType.Double).set_modelling_rule(True)
longitude = common_Location_type.add_variable(idx, "Longitude", "", ua.VariantType.Double).set_modelling_rule(True)

#define the object building
area_variable = common_Building_type.add_property(idx, "BuildingArea", "", ua.VariantType.Float).set_modelling_rule(True)
name_variable = common_Building_type.add_property(idx, "BuildingName", "", ua.VariantType.String).set_modelling_rule(True)
ID_variable = common_Building_type.add_property(idx, "BuildingID", "", ua.VariantType.Float).set_modelling_rule(True)

#define the object device
model_variable = common_Device_type.add_property(idx, "DeviceModel", "", ua.VariantType.String).set_modelling_rule(True)
manufacturer_variable = common_Device_type.add_property(idx, "DeviceManufacturer", "", ua.VariantType.String).set_modelling_rule(True)
ID_variable = common_Device_type.add_property(idx, "DeviceID", "", ua.VariantType.String).set_modelling_rule(True)
state_variable = common_Device_type.add_variable(idx, "DeviceState", "Off", ua.VariantType.String).set_modelling_rule(True)
common_Device_type.add_method(idx, "TurnOn", turn_on, [], [], []).set_modelling_rule(True)
common_Device_type.add_method(idx, "TurnOff", turn_off, [], [], []).set_modelling_rule(True)

#define the object measurement
timeStamp_variable = common_Measurement_type.add_variable(idx, "MeasurementTimeStamp", "", ua.VariantType.DateTime).set_modelling_rule(True)
value_variable = common_Measurement_type.add_variable(idx, "MeasurementValue", "", ua.VariantType.Double).set_modelling_rule(True)
timeInterval_variable = common_Measurement_type.add_variable(idx, "MeasurementTimeInterval", "", ua.VariantType.DateTime).set_modelling_rule(True)
unit_variable = common_Measurement_type.add_variable(idx, "MeasurementUnit", "", ua.VariantType.String).set_modelling_rule(True)

#define the object service type
service_name_variable = common_Service_type.add_property(idx, "ServiceName", "", ua.VariantType.String).set_modelling_rule(True)

#define the object weather
wind_speed = common_Weather_type.add_variable(idx, "WindSpeed", "", ua.VariantType.Float).set_modelling_rule(True)
wind_direction = common_Weather_type.add_variable(idx, "WindDirection", ua.VariantType.Float).set_modelling_rule(True)
cloud_cover = common_Weather_type.add_variable(idx, "CloudCoverIndex", ua.VariantType.Float).set_modelling_rule(True)
daytime = common_Weather_type.add_variable(idx, "DayTime", datetime.utcnow()).set_modelling_rule(True)
humidity = common_Weather_type.add_variable(idx, "Humidity", ua.VariantType.Float).set_modelling_rule(True)
temperature = common_Weather_type.add_variable(idx, "Temperature", ua.VariantType.Float).set_modelling_rule(True)

machines = ["Machine1", "Machine2", "Machine3"]
metering_points = ["EnergyMeter1", "EnergyMeter2", "EnergyMeter3"]
machine_data_objects = {}
metering_points_data_objects = {}

#function to add metering points to the machine objects
def add_metering_point_objects_to_machine_folder(metering_point, folder):
    metering_points_data_objects[metering_point] = folder.add_object(idx, f"{metering_point}", objecttype=common_Device_type)
    meteringservice = metering_points_data_objects[metering_point].add_object(idx, "MeteringService", objecttype = common_Service_type)
    meteringservice.add_object(idx, "CurrentMeasurement", objecttype = common_Measurement_type)
    meteringservice.add_method(idx, "GetAverageDailyConsumption", dailyAverage, [], [], []).set_modelling_rule(True)
    meteringservice.add_method(idx, "GetAverageMonthlyConsumption", monthlyAverage, [], [], []).set_modelling_rule(True)

#function to add machines to the machine folder
def add_machine_objects_to_building(machine_name, folder):
    machine_data_objects[machine_name] = folder.add_object(idx, f"{machine_name}", objecttype=common_Device_type)
    service = machine_data_objects[machine_name].add_object(idx, "ServiceOffered", objecttype = common_Service_type)
    MP_folder = machine_data_objects[machine_name].add_folder(idx, "MeteringPoints")
    for metering_point in metering_points:
        add_metering_point_objects_to_machine_folder(metering_point, MP_folder)

building = root.add_object(idx, "Building", objecttype=common_Building_type)
building.add_object(idx, "BuildingLocation", objecttype = common_Location_type)
building.add_object(idx, "Weather", objecttype=common_Weather_type)
machine_folder = building.add_folder(idx, "Machines")

for machine_name in machines:
    add_machine_objects_to_building(machine_name, machine_folder)


#server.export_xml_by_ns('Energy_meter_Model.xml',namespaces="OPCUA_SERVER")

server.start()



