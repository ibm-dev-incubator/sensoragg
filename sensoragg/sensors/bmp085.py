import time


class BMP085(object):
    ADDRESS = 0x77

    CAL_AC5 = 32757
    CAL_AC6 = 23153
    CAL_MC = 8711
    CAL_MD = 2868

    REG_CAL_AC5 = 0xB2
    REG_CAL_AC6 = 0xB4
    REG_CAL_MC = 0xBC
    REG_CAL_MD = 0xBE

    REG_CONTROL = 0xF4
    REG_TEMPDATA = 0xF6

    CMD_READTEMP = 0x2E

    def __init__(self, i2c_bus):
        self._bus = i2c_bus
        self._load_calibration()

    def read_S16BE(self, register):
        return self._bus.read_S16BE(self.ADDRESS, register)

    def read_U16BE(self, register):
        return self._bus.read_U16BE(self.ADDRESS, register)

    def _load_calibration(self):
        self.CAL_AC5 = self.read_U16BE(self.REG_CAL_AC5)
        self.CAL_AC6 = self.read_U16BE(self.REG_CAL_AC6)
        self.CAL_MC = self.read_S16BE(self.REG_CAL_MC)
        self.CAL_MD = self.read_S16BE(self.REG_CAL_MD)

    def get_uncompensated_temp(self):
        self._bus.write_byte_data(self.ADDRESS, self.REG_CONTROL,
                                  self.CMD_READTEMP)
        time.sleep(.05)
        return self.read_S16BE(self.REG_TEMPDATA)

    def get_temperature(self):
        UT = self.get_uncompensated_temp()
        print(UT)
        X1 = ((UT - self.CAL_AC6) * self.CAL_AC5) >> 15
        X2 = (self.CAL_MC << 11) // (X1 + self.CAL_MD)
        B5 = X1 + X2
        return ((B5 + 8) >> 4) / 10.0
