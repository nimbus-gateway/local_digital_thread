import asyncio
import copy
import logging
from datetime import datetime
import time
from math import sin
from asyncua import ua, uamethod, Server

class SubHandler:
    """
    Subscription Handler. To receive events from server for a subscription
    """
    def datachange_notification(self, node, val, data):
        _logger.warning("Python: New data change event %s %s", node, val)

    def event_notification(self, event):
        _logger.warning("Python: New event %s", event)

class MyOpcServer:
    def __init__(self):
        self.server = Server()

    async def initialize_server(self):
        await self.server.init()
        self.server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
        self.server.set_server_name("FreeOpcUa Example Server")
        self.server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign
        ])

        uri = "http://examples.freeopcua.github.io"
        self.idx = await self.server.register_namespace(uri)

        dev = await self.server.nodes.base_object_type.add_object_type(self.idx, "MyDevice")
        await (await dev.add_variable(self.idx, "sensor1", 1.0)).set_modelling_rule(True)
        await (await dev.add_property(self.idx, "device_id", "0340")).set_modelling_rule(True)
        ctrl = await dev.add_object(self.idx, "controller")
        await ctrl.set_modelling_rule(True)
        await (await ctrl.add_property(self.idx, "state", "Idle")).set_modelling_rule(True)

        # ... (continued from original code)

    async def start_server(self):
        async with self.server:
            print("Available loggers are: ", logging.Logger.manager.loggerDict.keys())
            await self._start_update_loop()

    async def _start_update_loop(self):
        while True:
            await asyncio.sleep(0.1)
            await self.server.write_attribute_value(self.myvar.nodeid, ua.DataValue(sin(time.time())))

    @uamethod
    def multiply(self, parent, x, y):
        _logger.warning("multiply method call with parameters: %s %s", x, y)
        return x * y

    async def run(self):
        await self.initialize_server()
        # await self.run_example()

    # async def run_example(self):
    #     # ... (continued from original code)
    #     continue	


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _logger = logging.getLogger(__name__)
    opc_server = MyOpcServer()
    asyncio.run(opc_server.run())
