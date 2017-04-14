import argparse
import sys

from smbus2 import SMBus

def parse_args(argv):
    parser = argparse.ArgumentParser(description='Sensor aggregator.')

    parser.add_argument('i2c_bus',
                        help='I2C Bus number',
                        type=int)

    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])

    bus = SMBus(args.i2c_bus)
    bus.read_byte_data(0x77, 0xF6)
    import pdb;pdb.set_trace()
