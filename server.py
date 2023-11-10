import asyncio
import copy
import logging
from datetime import datetime
import time
from math import sin
import os
from app.config.config import Config
from comms.coms import RestClient


from asyncua import ua, uamethod, Server


_logger = logging.getLogger(__name__)


# LOCAL DIGITAL THREAD VARIABLES
config_instance = Config("app/config/config.yaml")
opc_config = config_instance.get_opc_config()
api_config = config_instance.get_api_config()
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

    input = {'nodeid': current_measurement.nodeid.Identifier, 'mapping': meter['MeteringService']['CurrentMeasurement']}
    api.post('addNode', input)
    await (await meteringservice.add_method(idx, "GetAverageDailyConsumption", dailyAverage, [], [], [])).set_modelling_rule(True)
    await (await meteringservice.add_method(idx, "GetAverageMonthlyConsumption", monthlyAverage, [], [], [])).set_modelling_rule(True)
    
    

#function to add machines to the machine folder
async def add_machine_objects_to_building(idx, machine_name, folder, energy_meters, objects_list):
  
    machine_data_objects[machine_name] = await folder.add_object(idx, f"{machine_name}", objecttype=objects_list['device'])
    service = await machine_data_objects[machine_name].add_object(idx, "ServiceOffered", objecttype = objects_list['service'])
    MP_folder = await machine_data_objects[machine_name].add_folder(idx, "Energy Meters")
    for meters in energy_meters:
        await add_metering_point_objects_to_machine_folder(idx, meters, MP_folder, objects_list)




async def main():

    server = Server()
    await server.init()
    # server.disable_clock()  #for debuging
    # server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")

    url = opc_config['serverurl']
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
    area_variable = await (await common_Building_type.add_property(idx, "BuildingArea", "", ua.VariantType.Float)).set_modelling_rule(True)
    name_variable = await (await common_Building_type.add_property(idx, "BuildingName", "", ua.VariantType.String)).set_modelling_rule(True)
    ID_variable = await (await common_Building_type.add_property(idx, "BuildingID", "", ua.VariantType.Float)).set_modelling_rule(True)


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
    timeInterval_variable = await common_Measurement_type.add_variable(idx, "MeasurementTimeInterval", "", ua.VariantType.DateTime)
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
    pressure = await (await common_Weather_type.add_variable(idx, "AtmosphoricPressure", 0.0, ua.VariantType.Float)).set_modelling_rule(True)
    cloudage = await (await common_Weather_type.add_variable(idx, "Cloudage", 0.0, ua.VariantType.Float)).set_modelling_rule(True)
    daytime = await (await common_Weather_type.add_variable(idx, "DayTime", datetime.utcnow())).set_modelling_rule(True)
    percipitation = await (await common_Weather_type.add_variable(idx, "Precipitation", 0.0, ua.VariantType.Float)).set_modelling_rule(True)
    visibility = await (await common_Weather_type.add_variable(idx, "Visibility", 0.0, ua.VariantType.Float)).set_modelling_rule(True)


   
    

    
    # calling the API and getting the mapping
    cwd = os.path.abspath('./')

    response = api.get('mapping')

    if response.status_code == 200:
        mapping = response.json()
        print("Response from API: ", mapping)
    else:
        exit()


    buildings = mapping['Buildings']
    


    for Building in buildings:

        building = await root.add_object(idx, Building['BuildingName'], objecttype=common_Building_type)
        await building.add_object(idx, "BuidlingLocation", objecttype=common_Location_type)
        await building.add_object(idx, "Weather", objecttype=common_Weather_type)
        machine_folder = await building.add_folder(idx, "Machines")

        print(Building)
        for machine in Building['Machines']:
            print("Adding Machine!!!!!!!!!!!!!!!")

            await add_machine_objects_to_building(idx, machine['DeviceID'], machine_folder, machine['EnergyMeters'], objects_list)

    



    # w = await root.add_object(idx, "Weather", objecttype=common_Weather_type)

    # # create a new node type we can instantiate in our address space
    # dev = await server.nodes.base_object_type.add_object_type(idx, "MyDevice")
    # await (await dev.add_variable(idx, "sensor1", 1.0)).set_modelling_rule(True)
    # await (await dev.add_property(idx, "device_id", "0340")).set_modelling_rule(True)
    # ctrl = await dev.add_object(idx, "controller")
    # await ctrl.set_modelling_rule(True)
    # await (await ctrl.add_property(idx, "state", "Idle")).set_modelling_rule(True)

    # # populating our address space

    # # First a folder to organise our nodes
    # myfolder = await server.nodes.objects.add_folder(idx, "myEmptyFolder")
    # # instanciate one instance of our device
    # mydevice = await server.nodes.objects.add_object(idx, "Device0001", dev)
    # mydevice_var = await mydevice.get_child(
    #     [f"{idx}:controller", f"{idx}:state"]
    # )  # get proxy to our device state variable
    # # create directly some objects and variables
    # myobj = await server.nodes.objects.add_object(idx, "MyObject")
    # myvar = await myobj.add_variable(idx, "MyVariable", 6.7)
    # await myvar.set_writable()  # Set MyVariable to be writable by clients
    # mystringvar = await myobj.add_variable(idx, "MyStringVariable", "Really nice string")
    # await mystringvar.set_writable()  # Set MyVariable to be writable by clients
    # mydtvar = await myobj.add_variable(idx, "MyDateTimeVar", datetime.utcnow())
    # await mydtvar.set_writable()  # Set MyVariable to be writable by clients
    # myarrayvar = await myobj.add_variable(idx, "myarrayvar", [6.7, 7.9])
    # myuintvar = await myobj.add_variable(idx, "myuintvar", ua.UInt16(4))
    # await myobj.add_variable(idx, "myStronglytTypedVariable", ua.Variant([], ua.VariantType.UInt32))
    # await myarrayvar.set_writable(True)
    # myprop = await myobj.add_property(idx, "myproperty", "I am a property")


    # starting!
    async with server:
        print("Available loggers are: ", logging.Logger.manager.loggerDict.keys())
        # enable following if you want to subscribe to nodes on server side
        # handler = SubHandler()
        # sub = await server.create_subscription(500, handler)
        # handle = await sub.subscribe_data_change(myvar)
        # trigger event, all subscribed clients wil receive it
        # var = await myarrayvar.read_value()  # return a ref to value in db server side! not a copy!
        # var = copy.copy(
        #     var
        # )  # WARNING: we need to copy before writting again otherwise no data change event will be generated
        # var.append(9.3)
        #  await myarrayvar.write_value(var)
        # await mydevice_var.write_value("Running")
        # await myevgen.trigger(message="This is BaseEvent")
        # write_attribute_value is a server side method which is faster than using write_value
        # but than methods has less checks
        # await server.write_attribute_value(myvar.nodeid, ua.DataValue(0.9))

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
