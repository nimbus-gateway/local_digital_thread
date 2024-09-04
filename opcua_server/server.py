import asyncio
import copy
import logging
from datetime import datetime
import time
from math import sin
import os
from config.config import Config
from comms.coms import RestClient


from asyncua import ua, uamethod, Server
from asyncua.common.xmlexporter import XmlExporter


_logger = logging.getLogger(__name__)


# LOCAL DIGITAL THREAD VARIABLES
config_instance = Config()
conf = config_instance.get_config()
opc_config = conf['opc']
api_config = conf['data_source_manager']
api = RestClient("http://{0}:{1}/".format(api_config['host'], api_config['port']))


common_Weather_type = None
common_ElectricEnergyMeasurement_type = None
common_Energy_type = None
common_MeteringPoint_type = None
common_Machine_type = None
common_Building_type = None
common_TimeSeriesMeasurement_type = None


machines = ["Machine1", "Machine2", "Machine3"]
metering_points = ["EnergyMeter1", "EnergyMeter2", "EnergyMeter3"]
machine_data_objects = {}
metering_points_data_objects = {}


# machine_data_objects = {}
# metering_points_data_objects = {}
# energy_type_objects = {}
# energy_types = ["Electric", "Gas", "Thermal"]

# energy_variable_objects = {}
# energy_variables = ["Current", "Power", "Voltage"]


#methods to be exposed through server - to be implemented
def dailyAverage(parent, inputs, outputs):
    print("Summary as follows")
    return []

def monthlyAverage(parent, inputs, outputs):
    print("Summary as follows")
    return []

# method for turning the device on
def turn_on(parent, inputs, outputs):
    # state_variable.set_value("On")
    return []

#method for turning the device off
def turn_off(parent, inputs, outputs):
    # state_variable.set_value("Off")
    return []





#function to add metering points to the machine objects
async def add_metering_point_objects_to_machine_folder(idx, meter, folder, objects_list):
    metering_points_data_objects[meter['DeviceID']] = await folder.add_object(idx, f"{meter['DeviceID']}", objecttype=objects_list['device'])
    meteringservice = await metering_points_data_objects[meter['DeviceID']].add_object(idx, "MeteringService", objecttype = objects_list['service'])

    current_measurement = await meteringservice.add_object(idx, "CurrentMeasurement", objecttype = objects_list['measurement'])

    input = {'reference_id': meter['DeviceID'],'nodeid': current_measurement.nodeid.Identifier, 'mapping': meter['MeteringService']['CurrentMeasurement']}
    api.post('addNode', input)
    await (await meteringservice.add_method(idx, "GetAverageDailyConsumption", dailyAverage, [], [], [])).set_modelling_rule(True)
    await (await meteringservice.add_method(idx, "GetAverageMonthlyConsumption", monthlyAverage, [], [], [])).set_modelling_rule(True)
    
    

#function to add machines to the machine folder
async def add_machine_objects_to_building(idx, machine_name, folder, energy_meters, objects_list):
    machine = machine_data_objects[machine_name] = await folder.add_object(idx, f"{machine_name}", objecttype=objects_list['device'])
    service = await machine_data_objects[machine_name].add_object(idx, "ServiceOffered", objecttype = objects_list['service'])
    MP_folder = await machine_data_objects[machine_name].add_folder(idx, "Energy Meters")
    for meters in energy_meters:
        await add_metering_point_objects_to_machine_folder(idx, meters, MP_folder, objects_list)

    return machine

async def list_all_nodes(root):
    """
    List all nodes in the OPC UA server starting from the given root node.
    """
    nodes = []

    async def browse_nodes(node):
        nodes.append(node)
        children = await node.get_children()
        for child in children:
            await browse_nodes(child)

    await browse_nodes(root)
    return nodes

async def export_nodes_to_xml(server, node_list):
    exporter = XmlExporter(server)
    await exporter.build_etree(node_list)
    await exporter.write_xml('ua-export.xml')


async def main():

    server = Server()
    await server.init()
    # server.disable_clock()  #for debuging
    # server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")

    url = opc_config['server_url']
    server.set_endpoint(url)
    server.set_server_name(opc_config['servername'])
    # set all possible endpoint policies for clients to connect through
    server.set_security_policy(        [
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign,
        ]
    )

   
     # setup our own namespace
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    root = await server.nodes.objects.add_folder(idx, "Local Digital Thread")


    #define the object types
    common_Weather_type = await server.nodes.base_object_type.add_object_type(idx, "CommonWeather")
    common_Device_type = await server.nodes.base_object_type.add_object_type(idx, "CommonDevice")
    common_Building_type = await server.nodes.base_object_type.add_object_type(idx, "CommonBuilding")
    common_Location_type = await server.nodes.base_object_type.add_object_type(idx, "CommonLocation")
    common_Measurement_type = await server.nodes.base_object_type.add_object_type(idx, "CommonMeasurementType")
    common_MeteringProperty_type = await server.nodes.base_object_type.add_object_type(idx, "CommonMeteringPropertyType")
    common_Service_type = await server.nodes.base_object_type.add_object_type(idx, "CommonService")

    objects_list = {'building': common_Building_type, 'device': common_Device_type, 'weather': common_Weather_type, 'location': common_Location_type,
                    'measurement': common_Measurement_type, 'metering_property': common_MeteringProperty_type, 'service': common_Service_type}
    

    #define the object location
    latitude = await (await common_Location_type.add_variable(idx, "Latitude", "", ua.VariantType.Double)).set_modelling_rule(True)
    longitude = await (await common_Location_type.add_variable(idx, "Longitude", "", ua.VariantType.Double)).set_modelling_rule(True)


    #define the object building
    area_variable = await (await common_Building_type.add_property(idx, "BuildingArea", "", ua.VariantType.String)).set_modelling_rule(True)
    name_variable = await (await common_Building_type.add_property(idx, "BuildingName", "", ua.VariantType.String)).set_modelling_rule(True)
    ID_variable = await (await common_Building_type.add_property(idx, "BuildingID", "", ua.VariantType.String)).set_modelling_rule(True)


    #define the object device
    model_variable = await (await common_Device_type.add_property(idx, "DeviceModel", "", ua.VariantType.String)).set_modelling_rule(True)
    manufacturer_variable = await (await common_Device_type.add_property(idx, "DeviceManufacturer", "", ua.VariantType.String)).set_modelling_rule(True)
    ID_variable = await (await common_Device_type.add_property(idx, "DeviceID", "", ua.VariantType.String)).set_modelling_rule(True)
    state_variable = await (await common_Device_type.add_variable(idx, "DeviceState", "Off", ua.VariantType.String)).set_modelling_rule(True)
    await (await common_Device_type.add_method(idx, "TurnOn", turn_on, [], [], [])).set_modelling_rule(True)
    await (await common_Device_type.add_method(idx, "TurnOff", turn_off, [], [], [])).set_modelling_rule(True)

    # current_datetime = datetime.now()
    ua_datetime = ua.win_epoch_to_datetime(int(time.time()))

    #define the object measurement
    timeStamp_variable = await common_Measurement_type.add_variable(idx, "MeasurementTimeStamp", ua_datetime, ua.VariantType.DateTime)
    value_variable = await common_Measurement_type.add_variable(idx, "MeasurementValue", 0, ua.VariantType.Double)
    timeInterval_variable = await common_Measurement_type.add_variable(idx, "MeasurementTimeInterval", "", ua.VariantType.String)
    unit_variable = await common_Measurement_type.add_variable(idx, "MeasurementUnit", "", ua.VariantType.String)

    await timeStamp_variable.set_modelling_rule(True)
    await value_variable.set_modelling_rule(True)
    await timeInterval_variable.set_modelling_rule(True)
    await unit_variable.set_modelling_rule(True)

    await timeStamp_variable.set_writable(True)
    await value_variable.set_writable(True)
    await timeInterval_variable.set_writable(True)
    await unit_variable.set_writable(True)

    

    #define the object service type
    service_name_variable = await (await common_Service_type.add_property(idx, "ServiceName", "", ua.VariantType.String)).set_modelling_rule(True)

    #define the object weather
    condition = await (await common_Weather_type.add_variable(idx, "WeatherCondition", "", ua.VariantType.String)).set_modelling_rule(True)
    pressure = await (await common_Weather_type.add_variable(idx, "AtmosphoricPressure", 0, ua.VariantType.Double)).set_modelling_rule(True)
    cloudage = await (await common_Weather_type.add_variable(idx, "Cloudage", 0, ua.VariantType.Double)).set_modelling_rule(True)
    daytime = await (await common_Weather_type.add_variable(idx, "DayTime", datetime.utcnow())).set_modelling_rule(True)
    percipitation = await (await common_Weather_type.add_variable(idx, "Precipitation", 0, ua.VariantType.Double)).set_modelling_rule(True)
    visibility = await (await common_Weather_type.add_variable(idx, "Visibility", 0, ua.VariantType.Double)).set_modelling_rule(True)


   
    

    
    # calling the API and getting the mapping
    cwd = os.path.abspath('./')
    
    print("deleting existing node information from the data source manager..!!")
    response = api.delete('removeNodes')

        
    response = api.get('mapping')

    print("======response=====")
    print(response)

    if response.status_code == 200:
        mapping = response.json()['data']
        print("Response from API: ", mapping)
    else:
        print("exit due to status code :" + str(response.status_code))
        exit()


    buildings = mapping['Buildings']
    


    for Building in buildings:

        building = await root.add_object(idx, Building['BuildingName'], objecttype=common_Building_type)

        # setting building variable values
        var = await building.get_child(["2:BuildingID"])
        await var.set_value(Building['BuildingID'])
        var = await building.get_child(["2:BuildingName"])
        await var.set_value(Building['BuildingName'])
        var = await building.get_child(["2:BuildingArea"])
        await var.set_value(Building['BuildingArea'])


        # set values for Building Location
        location = await building.add_object(idx, "BuidlingLocation", objecttype=common_Location_type)
        var = await location.get_child(["2:Latitude"])
        await var.set_value(float(Building['BuildingLocation']['Latitude']))

        var = await location.get_child(["2:Longitude"])
        await var.set_value(float(Building['BuildingLocation']['Longitude']))


         # set values for weather data
        weather = await building.add_object(idx, "Weather", objecttype=common_Weather_type)
        var = await weather.get_child(["2:AtmosphoricPressure"])
        print(Building['Weather']['AtmosphoricPressure'])
        await var.set_value(float(5.02))
        var = await weather.get_child(["2:Cloudage"])
        await var.set_value(float(Building['Weather']['Cloudage']))
        var = await weather.get_child(["2:DayTime"])
        await var.set_value(datetime.utcnow())
        var = await weather.get_child(["2:Precipitation"])
        await var.set_value(float(Building['Weather']['Precipitation']))
        var = await weather.get_child(["2:Visibility"])
        await var.set_value(float(Building['Weather']['Visibility']))
        var = await weather.get_child(["2:WeatherCondition"])
        await var.set_value(Building['Weather']['WeatherCondition'])

        machine_folder = await building.add_folder(idx, "Machines")

        print(Building)
        for machine in Building['Machines']:
            print("Adding Machine!!!!!!!!!!!!!!!")

            machine_obj = await add_machine_objects_to_building(idx, machine['DeviceID'], machine_folder, machine['EnergyMeters'], objects_list)

            # set values of machine object
            var = await machine_obj.get_child(["2:DeviceID"])
            await var.set_value(machine['DeviceID'])
            var = await machine_obj.get_child(["2:DeviceManufacturer"])
            await var.set_value(machine['DeviceManufacturer'])
            var = await machine_obj.get_child(["2:DeviceModel"])
            await var.set_value(machine['DeviceModel'])

            for meter in machine['EnergyMeters']:
                meter_obj = metering_points_data_objects[meter['DeviceID']]
                var = await meter_obj.get_child(["2:DeviceID"])
                await var.set_value(meter['DeviceID'])
                var = await meter_obj.get_child(["2:DeviceManufacturer"])
                await var.set_value(meter['DeviceManufacturer'])
                var = await meter_obj.get_child(["2:DeviceModel"])
                await var.set_value(meter['DeviceModel'])

                metering_service_obj = await meter_obj.get_child(["2:MeteringService"])
                current_measurement_obj = await metering_service_obj.get_child(["2:CurrentMeasurement"])
                var = await current_measurement_obj.get_child(["2:MeasurementTimeInterval"])
                await var.set_value(meter['MeteringService']['CurrentMeasurement']['MeasurementTimeInterval'])
                var = await current_measurement_obj.get_child(["2:MeasurementUnit"])
                await var.set_value(meter['MeteringService']['CurrentMeasurement']['MeasurementUnit'])


    # exporter = XmlExporter(server)
    # await exporter.build_etree(node_list, ['http://myua.org/test/'])

    # node_list = await list_all_nodes(server.get_root_node()) 
    # #[server.nodes.objects, server.nodes.types]
    # await export_nodes_to_xml(server, node_list)





    # starting!
    async with server:
        print("Available loggers are: ", logging.Logger.manager.loggerDict.keys())

        while True:
            await asyncio.sleep(0.1)
            # await server.write_attribute_value(myvar.nodeid, ua.DataValue(sin(time.time())))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # optional: setup logging
    # logger = logging.getLogger("asyncua.address_space")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.internal_server")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.binary_server_asyncio")
    # logger.setLevel(logging.DEBUG)
    # logger = logging.getLogger("asyncua.uaprocessor")
    # logger.setLevel(logging.DEBUG)

    asyncio.run(main())
