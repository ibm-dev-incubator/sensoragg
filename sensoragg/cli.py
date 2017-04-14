import argparse
import sys

from smbus2 import SMBus

from sensoragg import i2c
from sensoragg.sensors import bmp085

def parse_args(argv):
    parser = argparse.ArgumentParser(description='Sensor aggregator.')

    parser.add_argument('i2c_bus',
                        help='I2C Bus number',
                        type=int)

    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])

    with i2c.I2CBus(args.i2c_bus) as bus:
        sensor = bmp085.BMP085(bus)
        temp = sensor.get_temperature()
        print(temp)
