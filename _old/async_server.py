import asyncio
import copy
import logging
from datetime import datetime
import time
from math import sin
import os
from app.config.config import Config
from coms import RestClient


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


machine_data_objects = {}
metering_points_data_objects = {}
energy_type_objects = {}
energy_types = ["Electric", "Gas", "Thermal"]

energy_variable_objects = {}
energy_variables = ["Current", "Power", "Voltage"]



#function to add energy measurement types to the energy type object
async def add_energy_type_to_energy_folder(idx, energy_type, folder, enery_objects,  objects_list):
    energy_type_objects[energy_type] = await folder.add_object(idx, f"{energy_type}", objecttype=objects_list['electric_measurement'])

    
    power_object = await energy_type_objects[energy_type].add_object(idx, "Power", objecttype=objects_list['time_series_measurement'])
    voltage_object = await energy_type_objects[energy_type].add_object(idx, "Voltage", objecttype=objects_list['time_series_measurement'])
    current_object = await energy_type_objects[energy_type].add_object(idx, "Current", objecttype=objects_list['time_series_measurement'])

    print("Power Object......", power_object)

    # Updating the node IDs in the mapping
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
async def add_metering_point_objects_to_machine_folder(idx, metering_point, folder, objects_list):
    metering_points_data_objects[metering_point['MateringPointName']] = await folder.add_object(idx, f"{metering_point['MateringPointName']}", objecttype=objects_list['metering_point'])
    energy_folder = await metering_points_data_objects[metering_point['MateringPointName']].add_folder(idx, "EnergyTypes")

    for energy_type in energy_types:
        await add_energy_type_to_energy_folder(idx, energy_type,energy_folder, metering_point['EnergyObject'], objects_list)

#function to add machines to the machine folder
async def add_machine_objects_to_building(idx, machine_name, folder, metering_points, objects_list):
    print("Common Machine", common_Machine_type)

    machine_data_objects[machine_name] = await folder.add_object(idx, f"{machine_name}", objecttype=objects_list['machine'])
    MP_folder = await machine_data_objects[machine_name].add_folder(idx, "MeteringPoints")
    for metering_point in metering_points:
        await add_metering_point_objects_to_machine_folder(idx, metering_point, MP_folder, objects_list)





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

    root = await server.nodes.objects.add_folder(idx, "MyInfoModel")

    #define the object types
    common_Weather_type = await server.nodes.base_object_type.add_object_type(idx, "CommonWeather")
    common_ElectricEnergyMeasurement_type = await server.nodes.base_object_type.add_object_type(idx, "ElectricEnergyMeasurement")
    common_Energy_type = await server.nodes.base_object_type.add_object_type(idx, "CommonEnergy")
    common_MeteringPoint_type = await server.nodes.base_object_type.add_object_type(idx, "CommonMeteringPoint")
    common_Machine_type = await server.nodes.base_object_type.add_object_type(idx, "CommonMachine")
    common_Building_type = await server.nodes.base_object_type.add_object_type(idx, "CommonBuilding")
    common_TimeSeriesMeasurement_type = await server.nodes.base_object_type.add_object_type(idx, "TimeSeriesMeasurement")

    objects_list = {'building': common_Building_type, 'machine': common_Machine_type, 'weather': common_Weather_type, 'time_series_measurement': common_TimeSeriesMeasurement_type,
                    'electric_measurement': common_ElectricEnergyMeasurement_type, 'metering_point': common_MeteringPoint_type}

    #define the object TimeSeries Measurement
    timestamp = await common_TimeSeriesMeasurement_type.add_variable(idx, "TimeStamp", "XXXX", ua.VariantType.String)
    value = await common_TimeSeriesMeasurement_type.add_variable(idx, "Value", 0.0, ua.VariantType.Float)

    await timestamp.set_writable()
    await timestamp.set_modelling_rule(True) 
    await value.set_writable()
    await value.set_modelling_rule(True) 

    #define the object weather
    condition = await (await common_Weather_type.add_variable(idx, "WeatherCondition", "", ua.VariantType.String)).set_modelling_rule(True)
    pressure = await (await common_Weather_type.add_variable(idx, "AtmosphoricPressure", 0.0, ua.VariantType.Float)).set_modelling_rule(True)
    cloudage = await (await common_Weather_type.add_variable(idx, "Cloudage", 0.0, ua.VariantType.Float)).set_modelling_rule(True)
    daytime = await (await common_Weather_type.add_variable(idx, "DayTime", datetime.utcnow())).set_modelling_rule(True)
    percipitation = await (await common_Weather_type.add_variable(idx, "Precipitation", 0.0, ua.VariantType.Float)).set_modelling_rule(True)
    visibility = await (await common_Weather_type.add_variable(idx, "Visibility", 0.0, ua.VariantType.Float)).set_modelling_rule(True)


    lock_variable = await (await common_ElectricEnergyMeasurement_type.add_variable(idx, "Lock", 0.0, ua.VariantType.Int32)).set_modelling_rule(True)
    # common_ElectricEnergyMeasurement_type.add_method(idx, "DailyConsumption", ConsumptionSummary, ["", "Return", "Float"], ["", "Input", "String"]).set_modelling_rule(True)
    # common_ElectricEnergyMeasurement_type.add_method(idx, "MonthlyConsumption", ConsumptionSummary, ["", "Return", "Float"], ["", "Input", "String"]).set_modelling_rule(True)

    #define the object metering point
    communication_protocol_variable = await (await common_MeteringPoint_type.add_variable(idx, "CommunicationProtocol", "", ua.VariantType.String)).set_modelling_rule(True)
    sampling_rate_variable = await (await common_MeteringPoint_type.add_variable(idx, "SamplingRate", 0.0, ua.VariantType.Float)).set_modelling_rule(True)

    #define the object machine
    name_variable = await (await common_Machine_type.add_property(idx, "Name", "", ua.VariantType.String)).set_modelling_rule(True)
    model_variable = await (await common_Machine_type.add_property(idx, "Model", "", ua.VariantType.String)).set_modelling_rule(True)
    machine_type_variable = await (await common_Machine_type.add_property(idx, "Type", "", ua.VariantType.String)).set_modelling_rule(True)
    machine_ID_variable = await (await common_Machine_type.add_property(idx, "ID", "", ua.VariantType.Int32)).set_modelling_rule(True)
    manufacturer_variable = await (await common_Machine_type.add_property(idx, "Manufacturer", "", ua.VariantType.String)).set_modelling_rule(True)
    status_variable = await (await common_Machine_type.add_variable(idx, "Status", "", ua.VariantType.String)).set_modelling_rule(True)
    location_variable = await (await common_Machine_type.add_property(idx, "BuildingName", "", ua.VariantType.String)).set_modelling_rule(True)


    #define the object building
    location_variable = await (await common_Building_type.add_property(idx, "Coordinates", "", ua.VariantType.String)).set_modelling_rule(True)
    area_variable = await (await common_Building_type.add_property(idx, "Area", "", ua.VariantType.Float)).set_modelling_rule(True)
    address_variable = await (await common_Building_type.add_property(idx, "Address", "", ua.VariantType.String)).set_modelling_rule(True)

    

    
    # calling the API and getting the mapping
    cwd = os.path.abspath('./')

    response = api.get('getMapping')

    if response.status_code == 200:
        mapping = response.json()
        print("Response from API: ", mapping)
    else:
        exit()


    buildings = mapping['Buildings']
    


    for Building in buildings:

        building = await root.add_object(idx, Building['BuildingName'], objecttype=common_Building_type)
        await building.add_object(idx, "Weather", objecttype=common_Weather_type)
        machine_folder = await building.add_folder(idx, "Machines")

        print(Building)
        for machine in Building['Machines']:
            print("Adding Machine!!!!!!!!!!!!!!!")

            await add_machine_objects_to_building(idx, machine['Name'], machine_folder, machine['MeteringPoints'], objects_list)

    



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
