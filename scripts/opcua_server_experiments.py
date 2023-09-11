from opcua import Server, ua, uamethod
from time import sleep
i=0

    # Create a server instance
server = Server()

    # Set server endpoint URL and port
url = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
server.set_endpoint(url)

servername = "Python-OPC-UA-Server"
server.set_server_name(servername)

    #Object Node and Variable Node Modelling
root_node = server.get_root_node()
object_node = server.get_objects_node()
idx = server.register_namespace("OPCUA_SERVER")
myobj = object_node.add_object(idx, "DA_UA")

Temp = myobj.add_variable(idx ,"Temperature",0,ua.VariantType.Float)
Pressure = myobj.add_variable(idx ,"Pressure",0,ua.VariantType.Float)
Flow = myobj.add_variable(idx ,"Flow",0,ua.VariantType.Float)
Flow_2 = myobj.add_variable(idx ,"Flow_2",0,ua.VariantType.Float)

server.export_xml_by_ns('Server_Model.xml',namespaces="OPCUA_SERVER")
server.start()

try:
    while 1:
        Temp.set_value(i*0.25,ua.VariantType.Float)
        Pressure.set_value(i*0.26,ua.VariantType.Float)
        Flow.set_value(i*0.27,ua.VariantType.Float)
        Flow_2.set_value(i*0.28,ua.VariantType.Float)
        sleep(1)
        i = i + 1
except KeyboardInterrupt:
    server.stop()

