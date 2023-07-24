#!/usr/bin/env python3
#
# Vendor:Product ID for Raspberry Pi Pico is 2E8A:0005
#
import argparse
import datetime
import textwrap
import time
from datetime import datetime, timezone
from datetime import timedelta
from random import randrange
from time import gmtime
import asyncio
from prettytable import PrettyTable
import json

import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo
from itertools import groupby
import synchro_protocol

parser = argparse.ArgumentParser(
    description='Communicate through the vortex'
)
parser.add_argument('--device-type',
                    required=False,
                    help='TARDIS or DISPLAY')

args = parser.parse_args()


# The aim is to get the client RTC clock ticking over its second field at exactly the right moment.
# Task 1: We want to see if we literally can change the second-tick-over to occur at different millisecond offsets
# within the second. Take multiple samples of supervisor ticks_ms % 1000 at RTC tick-over, before and after
# setting the clock - we should see a difference. We should be able to *set* the difference! If we can't, we can't
# achieve our aim. Assuming we can set the diff, maybe calibrate if we need an offset to get desired tick-over time.

# Function to get supervisor tick-over time? Call, blocks for up to 1 second, returns an 0-999 integer=ticks at rollover


# 1 cycle:
#   Server Send time, with deadline ms offset
#   client waits to deadline supervisorsefsdf
#   get time back (when client-clock ticks over second)
#   this will yield a diff
#
# Perform


class DeviceType:
    def __init__(self, name: str, port: str, known_usb_device_serial_numbers: dict[str, str]):
        self.name = name
        self.port = port
        self.known_usb_device_serial_numbers = known_usb_device_serial_numbers


class DeviceConnection:
    def __init__(self, device_type: DeviceType, port_info: ListPortInfo):
        self.device_type = device_type
        self.port_info = port_info
        self.name = f'{device_type.name} {device_type.known_usb_device_serial_numbers[port_info.serial_number]}'
        self.latest_diff: dict[str, float] = {}

    def latest_diff_summary(self) -> str:
        return ", ".join([f'{name} @ {time_diff(diff)}' for name, diff in sorted(self.latest_diff.items())])



# VID:PID for different devices:
# RPi Pico                  : 2E8A:0005
# Pimoroni Pico LiPo (16MB) : 2E8A:1003
# Keybow 2040               : 16D0:08C6

TARDIS_DEVICE = DeviceType(
    "TARDIS",
    "16D0:08C6",
    {
        'E6609103C342C02C': "PRIME"
    }
)
PASSPHRASE_DISPLAY_DEVICE = DeviceType(
    "Display", "2E8A:0005",
    {
        'e66118604b7b3827': "A",
        'e66118604b1c7722': "B"
    }
)

ALL_DEVICE_TYPES = [TARDIS_DEVICE, PASSPHRASE_DISPLAY_DEVICE]


# device_type = next(x for x in ALL_DEVICE_TYPES if x.name.casefold() == args.device_type.casefold())
#
# print(f'device_type: {device_type.name}')


def send_timecube(con):
    originalTime = datetime.now(timezone.utc)
    t = originalTime.replace(microsecond=0) + timedelta(seconds=2)
    millisToWaitForDeadline = int((t - originalTime) / timedelta(milliseconds=1))

    timeCube = synchro_protocol.encode({'ts': f'{t.isoformat().replace("+00:00", "Z")}', 'w': t.weekday(), 'dl': millisToWaitForDeadline})
    con.write(timeCube.encode("utf-8"))

    timeAfterSending = datetime.now(timezone.utc)
    print(f'transmit cycle took {timeAfterSending - originalTime}')
    print("Time sync epoch USB MSG: " + timeCube)


def time_diff(diff: float):
    return f'{"-" if diff < 0 else "+"}{abs(diff):.3f}s {"✅" if abs(diff) < 0.5 else "❌"}'

def handle_line(line: str, read_time: datetime, device_connection: DeviceConnection):
    prefix = "clock_report:"
    suffix = "Z"
    starts_with_prefix = line.startswith(prefix)
    ends_with_suffix = line.endswith(suffix)
    if starts_with_prefix and ends_with_suffix:
        name, timestamp = line.removeprefix(prefix).removesuffix(suffix).split("=")
        dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
        diff = (dt - read_time).total_seconds()
        device_connection.latest_diff[name] = diff
        # print(f"{read_time.time().isoformat(timespec='milliseconds')} : {device_connection.name} : {name} @ {time_diff(diff)}")
    else:
        # print(textwrap.indent(line, '> '))
        pass


async def monitor_device(device_connection: DeviceConnection):
    with serial.Serial(device_connection.port_info.device) as console:
        send_timecube(console)
        while True:
            # if randrange(800) == 0:
            #     send_timecube(console)

            read_time = datetime.now(timezone.utc)
            num_bytes = console.inWaiting()
            if num_bytes > 0:
                input_data: str = console.read(num_bytes).decode("utf-8")
                for line in input_data.splitlines():
                    handle_line(line, read_time, device_connection)
            await asyncio.sleep(0.001 / 2)


def find_devices() -> list[DeviceConnection]:
    return [DeviceConnection(dt, port_info) for port_info in list_ports.comports() for dt in ALL_DEVICE_TYPES if
            port_info.serial_number in dt.known_usb_device_serial_numbers]


async def main():
    print('Hello ...')
    await asyncio.sleep(0.1)
    print('... World!')

    all_devices = find_devices()
    for dt, device_conns_for_dt in groupby(all_devices, lambda dc: dc.device_type):
        print(dt.name)
        for device_conn in device_conns_for_dt:
            print(f'* {device_conn.port_info} - {device_conn.name}')

    for device_conn in all_devices:
        asyncio.create_task(monitor_device(device_conn))

    while True:
        all_clock_names = sorted(list(set().union(*[device_conn.latest_diff.keys() for device_conn in all_devices])))
        x = PrettyTable()
        x.field_names = ["Device"] + all_clock_names
        x.add_rows([[dc.name] + [time_diff(dc.latest_diff[n]) if n in dc.latest_diff else "" for n in all_clock_names] for dc in all_devices])
        print(x)

        # for device_conn in all_devices:
        #     print(f'{device_conn.name}\t: {device_conn.latest_diff_summary()}')
        await asyncio.sleep(10)


asyncio.run(main())
