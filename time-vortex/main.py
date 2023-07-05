#!/usr/bin/env python3
#
# Vendor:Product ID for Raspberry Pi Pico is 2E8A:0005
#
import datetime
import textwrap
from datetime import timezone, timedelta
from time import gmtime
import argparse

import serial
import time
from serial.tools import list_ports

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


class Device:
    def __init__(self, name: str, port: str):
        self.name = name
        self.port = port


# VID:PID for different devices:
# RPi Pico                  : 2E8A:0005
# Pimoroni Pico LiPo (16MB) : 2E8A:1003
# Keybow 2040               : 16D0:08C6

TARDIS_DEVICE = Device("TARDIS", "16D0:08C6")
PASSPHRASE_DISPLAY_DEVICE = Device("Display", "2E8A:0005")

ALL_DEVICE = [TARDIS_DEVICE, PASSPHRASE_DISPLAY_DEVICE]

device_type = next(x for x in ALL_DEVICE if x.name.casefold() == args.device_type.casefold())

print(f'device_type: {device_type.name}')


def send_timecube(con):
    global originalTime, t, millisToWaitForDeadline, timeCube
    originalTime = datetime.datetime.now(timezone.utc)
    t = originalTime.replace(microsecond=0) + datetime.timedelta(seconds=1)
    millisToWaitForDeadline = int((t - originalTime) / timedelta(milliseconds=1))
    # year, month, day, hour, minute, second, wday
    print("gmtime=" + str(gmtime()))
    timeCube = ",".join(
        [str(x) for x in [t.year, t.month, t.day, t.hour, t.minute, t.second, t.weekday(), millisToWaitForDeadline]])
    syncMSG = 'T' + timeCube + '_'
    console.write(bytes(syncMSG, "ascii"))

    timeAfterSending = datetime.datetime.now(timezone.utc)
    print("Raspberry Pi Pico found at " + str(picoSerialPort))
    print(f'Original time was\t{str(originalTime)}')
    print(f'Time after sending\t{str(timeAfterSending)}')
    print(f'Deadline will be\t{str(t)}')
    print(f'millisToWaitForDeadline were {millisToWaitForDeadline}')
    print(f'transmit cycle took {timeAfterSending - originalTime}')

    print("Time sync epoch USB MSG: " + syncMSG)
    print("t: " + str(t))
    time.sleep((t - datetime.datetime.now(timezone.utc)).total_seconds())
    print(f'Time is now {datetime.datetime.now(timezone.utc)}')


picoPorts = list(list_ports.grep(device_type.port))
if not picoPorts:
    print("No Raspberry Pi Pico found")
else:
    print(f"Found {device_type.name} device:")
    for port_info in picoPorts:
        print(f'* {port_info}')

    picoSerialPort = picoPorts[0].device

    with serial.Serial(picoSerialPort) as console:
        # send_timecube(console)

        while True:
            num_bytes = console.inWaiting()
            if num_bytes > 0:
                now = datetime.datetime.now()
                input_data: str = console.read(num_bytes).decode("utf-8")
                for line in input_data.splitlines():
                    prefix = "clock_check:"
                    suffix = "Z"
                    starts_with_prefix = line.startswith(prefix)
                    ends_with_suffix = line.endswith(suffix)
                    if starts_with_prefix and ends_with_suffix:
                        name, timestamp = line.removeprefix(prefix).removesuffix(suffix).split("=")
                        dt = datetime.datetime.fromisoformat(timestamp)
                        # print(f'dt={dt} now={now}')
                        print(f'{name}:{(dt - now).total_seconds():.3f}s')
                    # else:
                    #   print(textwrap.indent(line, '> '))
            time.sleep(0.01)
