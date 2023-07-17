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

import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

parser = argparse.ArgumentParser(
    description='Communicate through the vortex'
)
parser.add_argument('--device-type',
                    required=True,
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
    global originalTime, t, millisToWaitForDeadline, timeCube
    originalTime = datetime.now(timezone.utc)
    t = originalTime.replace(microsecond=0) + timedelta(seconds=1)
    millisToWaitForDeadline = int((t - originalTime) / timedelta(milliseconds=1))
    # year, month, day, hour, minute, second, wday
    print("gmtime=" + str(gmtime()))
    timeCube = ",".join(
        [str(x) for x in [t.year, t.month, t.day, t.hour, t.minute, t.second, t.weekday(), millisToWaitForDeadline]])
    syncMSG = 'T' + timeCube + '_'
    con.write(bytes(syncMSG, "ascii"))

    timeAfterSending = datetime.now(timezone.utc)
    print(f'Original time was\t{str(originalTime)}')
    print(f'Time after sending\t{str(timeAfterSending)}')
    print(f'Deadline will be\t{str(t)}')
    print(f'millisToWaitForDeadline were {millisToWaitForDeadline}')
    print(f'transmit cycle took {timeAfterSending - originalTime}')

    print("Time sync epoch USB MSG: " + syncMSG)
    print("t: " + str(t))
    time.sleep((t - datetime.now(timezone.utc)).total_seconds())
    print(f'Time is now {datetime.now(timezone.utc)}')


def handle_line(line: str, read_time: datetime, device_type: DeviceType):
    prefix = "clock_report:"
    suffix = "Z"
    starts_with_prefix = line.startswith(prefix)
    ends_with_suffix = line.endswith(suffix)
    if starts_with_prefix and ends_with_suffix:
        name, timestamp = line.removeprefix(prefix).removesuffix(suffix).split("=")
        dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
        diff = (dt - read_time).total_seconds()
        clock_diff = f'{"-" if diff < 0 else "+"}{abs(diff):.3f}s {"✅" if abs(diff) < 0.5 else "❌"}'
        print(f"{read_time.time().isoformat(timespec='milliseconds')} : {device_type.name} : {name} @ {clock_diff}")
    else:
        # print(textwrap.indent(line, '> '))
        pass


async def monitor_device(dt: DeviceType, port_info: ListPortInfo):
    with serial.Serial(port_info.device) as console:
        send_timecube(console)
        while True:
            # if randrange(800) == 0:
            #     send_timecube(console)

            read_time = datetime.now(timezone.utc)
            num_bytes = console.inWaiting()
            if num_bytes > 0:
                input_data: str = console.read(num_bytes).decode("utf-8")
                for line in input_data.splitlines():
                    handle_line(line, read_time, dt)
            await asyncio.sleep(0.001 / 2)


def find_devices() -> list[(DeviceType, ListPortInfo)]:
    return [(dt, port_info) for port_info in list_ports.comports() for dt in ALL_DEVICE_TYPES if port_info.serial_number in dt.known_usb_device_serial_numbers]

async def main():
    print('Hello ...')
    await asyncio.sleep(0.1)
    print('... World!')

    for dt, port_info in find_devices():
        print(f'dt name={dt.name}')
        print(f'* {port_info} - {dt.known_usb_device_serial_numbers[port_info.serial_number]}')
        asyncio.create_task(monitor_device(dt, port_info))

    while True:
        await asyncio.sleep(10)


asyncio.run(main())
