from smbus2 import SMBus


class I2CBusAlreadyRunning(Exception):
    pass


class I2CBus(object):
    def __init__(self, bus_id):
        self.bus_id = bus_id
        self._bus = None

    def __enter__(self):
        if self._bus is not None:
            raise I2CBusAlreadyRunning('I2C bus already running.')
        self._bus = SMBus(self.bus_id)
        return self

    def __exit__(self, *args):
        self._bus = None

    def read_byte_data(self, device, register):
        return self._bus.read_byte_data(device, register)

    def write_byte_data(self, device, register, data):
        return self._bus.write_byte_data(device, register, data)
