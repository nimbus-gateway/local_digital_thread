import sys
sys.path.insert(0, "..")
import time
import math
from datetime import timedelta


from opcua import ua, Server
from opcua.server.history_sql import HistorySQLite


print("Test Server")

def history_data_received_callback(self, history_data):
        # Store the new historical data in the database.
        for timestamp in history_data:
            # Convert the datetime.datetime object to a datetime.timedelta object.
            timedelta_object = timedelta(seconds=timestamp)

            # Store the timestamp and value in the database.
        print(history_data)
        print("in call back....")

        file_path = 'history.txt'


        # Open the file in write mode ('w')
        with open(file_path, 'w') as file:
            # Write the string to the file
            file.write('INSERT INTO history (timestamp, value) VALUES (?, ?)', (timestamp, timedelta_object.timedelta))

        # Commit the changes to the database.
        # self.db_conn.commit()



if __name__ == "__main__":

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our custom stuff
    objects = server.get_objects_node()

    # populating our address space
    myobj = objects.add_object(idx, "MyObject")
    myvar = myobj.add_variable(idx, "MyVariable", ua.Variant(0, ua.VariantType.Double))
    myvar.set_writable()  # Set MyVariable to be writable by clients

    # Configure server to use sqlite as history database (default is a simple memory dict)
    server.iserver.history_manager.set_storage(HistorySQLite("my_datavalue_history.sql"))

    server.history_data_received = history_data_received_callback

    # starting!
    server.start()

    server.historize_node_data_change(myvar, period=None, count=100)

    # enable data change history for this particular node, must be called after start since it uses subscription
    
    
    

    try:
        count = 0
        while True:
            time.sleep(1)
            count += 0.1
            myvar.set_value(math.sin(count))

    finally:
        # close connection, remove subscriptions, etc
        server.stop()