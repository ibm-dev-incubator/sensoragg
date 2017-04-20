import time


class BMP085(object):
    ADDRESS = 0x77

    CAL_AC1 = 408
    CAL_AC2 = -72
    CAL_AC3 = -14383
    CAL_AC4 = 32741
    CAL_AC5 = 32757
    CAL_AC6 = 23153
    CAL_B1 = 6190
    CAL_B2 = 4
    CAL_MC = 8711
    CAL_MD = 2868

    REG_CAL_AC1 = 0xAA
    REG_CAL_AC2 = 0xAC
    REG_CAL_AC3 = 0xAE
    REG_CAL_AC4 = 0xB0
    REG_CAL_AC5 = 0xB2
    REG_CAL_AC6 = 0xB4
    REG_CAL_B1 = 0xB6
    REG_CAL_B2 = 0xB8
    REG_CAL_MC = 0xBC
    REG_CAL_MD = 0xBE

    REG_CONTROL = 0xF4
    REG_TEMPDATA = 0xF6
    REG_PRESSUREDATA = 0xF6

    CMD_READTEMP = 0x2E
    CMD_READPRESSURE = 0x34

    def __init__(self, i2c_bus):
        self._bus = i2c_bus
        self._load_calibration()

    def read_byte_data(self, register):
        return self._bus.read_byte_data(self.ADDRESS, register)

    def write_byte_data(self, register, data):
        return self._bus.write_byte_data(self.ADDRESS, register, data)

    def read_S16BE(self, register):
        return self._bus.read_S16BE(self.ADDRESS, register)

    def read_U16BE(self, register):
        return self._bus.read_U16BE(self.ADDRESS, register)

    def _load_calibration(self):
        self.CAL_AC1 = self.read_S16BE(self.REG_CAL_AC1)
        self.CAL_AC2 = self.read_S16BE(self.REG_CAL_AC2)
        self.CAL_AC3 = self.read_S16BE(self.REG_CAL_AC3)
        self.CAL_AC4 = self.read_U16BE(self.REG_CAL_AC4)
        self.CAL_AC5 = self.read_U16BE(self.REG_CAL_AC5)
        self.CAL_AC6 = self.read_U16BE(self.REG_CAL_AC6)
        self.CAL_B1 = self.read_S16BE(self.REG_CAL_B1)
        self.CAL_B2 = self.read_S16BE(self.REG_CAL_B2)
        self.CAL_MC = self.read_S16BE(self.REG_CAL_MC)
        self.CAL_MD = self.read_S16BE(self.REG_CAL_MD)

    def get_uncompensated_temp(self):
        self.write_byte_data(self.REG_CONTROL, self.CMD_READTEMP)
        time.sleep(.05)
        return self.read_S16BE(self.REG_TEMPDATA)

    def get_uncompensated_pressure(self):
        self.write_byte_data(self.REG_CONTROL, self.CMD_READPRESSURE)
        time.sleep(.008)
        UP = self.read_U16BE(self.REG_PRESSUREDATA)
        lsb = self.read_byte_data(self.REG_PRESSUREDATA + 2)
        return (UP << 1) + (lsb >> 7)

    def get_temperature(self):
        UT = self.get_uncompensated_temp()
        B5 = self._calc_B5(UT)
        return ((B5 + 8) >> 4) / 10.0

    def _calc_B5(self, UT):
        # Conversion code taken from datasheet
        X1 = ((UT - self.CAL_AC6) * self.CAL_AC5) >> 15
        X2 = (self.CAL_MC << 11) // (X1 + self.CAL_MD)
        return X1 + X2

    def get_pressure(self):
        UT = self.get_uncompensated_temp()
        UP = self.get_uncompensated_pressure()
        B5 = self._calc_B5(UT)
        # Conversion code taken from datasheet
        B6 = B5 - 4000
        X1 = (self.CAL_B2 * (B6 ** 2) >> 12) >> 11
        X2 = (self.CAL_AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.CAL_AC1 * 4 + X3) << 1) + 2) // 4
        X1 = (self.CAL_AC3 * B6) >> 13
        X2 = (self.CAL_B1 * ((B6 ** 2) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.CAL_AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> 1)
        if B7 < 0x80000000:
            p = (B7 * 2) // B4
        else:
            p = (B7 // B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        return p + ((X1 + X2 + 3791) >> 4)
