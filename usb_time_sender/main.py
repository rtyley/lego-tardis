#!/usr/bin/env python3
#
# Vendor:Product ID for Raspberry Pi Pico is 2E8A:0005
#
from serial.tools import list_ports
import serial, time
from datetime import timezone, timedelta
import datetime
from time import gmtime
import textwrap

print("Hi there")
print(list_ports.comports())

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
        # syncMSG = 'T'+str(int(1000*t.timestamp()))
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

