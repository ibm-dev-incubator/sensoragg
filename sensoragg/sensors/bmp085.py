import time


class BMP085(object):
    ADDRESS = 0x77

    REG_CONTROL = 0xF4
    REG_TEMPDATA = 0xF6

    CMD_READTEMP = 0x2E

    def __init__(self, i2c_bus):
        self._bus = i2c_bus

    def get_temperature(self):
        self._bus.write_byte_data(self.ADDRESS, self.REG_CONTROL,
                                  self.CMD_READTEMP)
        time.sleep(.05)
        return self.read_byte_data(self.ADDRESS, self.REG_TEMPDATA)
