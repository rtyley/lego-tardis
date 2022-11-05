#!/usr/bin/env python3
#
# Vendor:Product ID for Raspberry Pi Pico is 2E8A:0005
#
import datetime
import textwrap
from datetime import timezone, timedelta
from time import gmtime

import serial
import time
from serial.tools import list_ports

print("Hi there")
print(list_ports.comports())

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

# VID:PID for different devices:
# RPi Pico                  : 2E8A:0005
# Pimoroni Pico LiPo (16MB) : 2E8A:1003
# Keybow 2040               : 16D0:08C6

picoPorts = list(list_ports.grep("16D0:08C6"))
if not picoPorts:
    print("No Raspberry Pi Pico found")
else:
    print("Found device")
    picoSerialPort = picoPorts[0].device
    originalTime = datetime.datetime.now(timezone.utc)
    t = originalTime.replace(microsecond=0) + datetime.timedelta(seconds=1)
    millisToWaitForDeadline = int((t - originalTime) / timedelta(milliseconds=1))

    # year, month, day, hour, minute, second, wday
    print("gmtime=" + str(gmtime()))
    timeCube = ",".join(
        [str(x) for x in [t.year, t.month, t.day, t.hour, t.minute, t.second, t.weekday(), millisToWaitForDeadline]])

    with serial.Serial(picoSerialPort) as console:
        syncMSG = 'T'+timeCube+'_'
        console.write(bytes(syncMSG, "ascii"))

        while True:
            num_bytes = console.inWaiting()
            if num_bytes > 0:
                input_data = console.read(num_bytes)
                print(textwrap.indent(input_data.decode("utf-8"), '> '))
            time.sleep(0.01)


    timeAfterSending = datetime.datetime.now(timezone.utc)
    print( "Raspberry Pi Pico found at "+str(picoSerialPort) )
    print(f'Original time was\t{str(originalTime)}')
    print(f'Time after sending\t{str(timeAfterSending)}')
    print(f'Deadline will be\t{str(t)}')
    print(f'millisToWaitForDeadline were {millisToWaitForDeadline}')
    print(f'transmit cycle took {timeAfterSending - originalTime}')

    print( "Time sync epoch USB MSG: "+syncMSG )
    print( "t: "+str(t) )
    time.sleep((t-datetime.datetime.now(timezone.utc)).total_seconds())
    print( f'Time is now {datetime.datetime.now(timezone.utc)}')

