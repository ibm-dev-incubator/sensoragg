import argparse
import base64
import http.client
import json
import sys
import urllib.parse

from smbus2 import SMBus

from sensoragg import i2c
from sensoragg.sensors import bmp085

def parse_args(argv):
    parser = argparse.ArgumentParser(description='Sensor aggregator.')

    parser.add_argument('i2c_bus',
                        help='I2C Bus number',
                        type=int)
    parser.add_argument('org_id',
                        help='Organization ID',
                        type=str)
    parser.add_argument('auth_token',
                        help='Authorization token',
                        type=str)
    parser.add_argument('device_type',
                        help='Watson IOT device type',
                        type=str)
    parser.add_argument('device_id',
                        help='Watson IOT device id',
                        type=str)

    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])

    userpass = 'use-token-auth:%s' % args.auth_token
    b64_userpass = base64.b64encode(userpass.encode('ascii')).decode('ascii')
    headers = {
        'Content-type': 'application/json',
        'Authorization': 'Basic %s' % b64_userpass
    }

    api_host = '%s.messaging.internetofthings.ibmcloud.com' % args.org_id
    ev_uri = '/api/v0002/device/types/%s/devices/%s/events/0' % (
        args.device_type, args.device_id
    )

    with i2c.I2CBus(args.i2c_bus) as bus:
        sensor = bmp085.BMP085(bus)
        temp = sensor.get_temperature()
        params = {
            'temperature': temp
        }
        print('%f' % temp)
        http_con = http.client.HTTPSConnection(api_host, port=8883)
        http_con.request('POST', ev_uri, headers=headers,
                         body=json.dumps(params))
        resp = http_con.getresponse()
        print(resp.code)
