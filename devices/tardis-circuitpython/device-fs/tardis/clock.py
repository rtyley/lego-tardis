import asyncio

import adafruit_ticks
import board
import adafruit_ds3231  # battery-backed RTC
import supervisor
import time
from sys import stdin
from select import select
from tardis.windows import set_all_windows
from adafruit_ticks import *
import rtc
import time

rp2040_rtc = rtc.RTC()

i2c = board.I2C()
batteryRTC = adafruit_ds3231.DS3231(i2c)

def set_rp2040_rtc_from_battery_rtc():
    for x in range(2):
        initial_battery_rtc_time = batteryRTC.datetime
        latest_battery_rtc_time = initial_battery_rtc_time
        while latest_battery_rtc_time == initial_battery_rtc_time:
            latest_battery_rtc_time = batteryRTC.datetime

    rp2040_rtc.datetime = latest_battery_rtc_time
    print(f'latest_battery_rtc_time: {latest_battery_rtc_time}')
    print(f'rp2040_rtc.datetime: {rp2040_rtc.datetime}')

async def watch_clock():
    print("Waiting for time signal....")
    while True:
        received_time_data_from_usb = readDeadlineAndTimeToDeadlineFromUSB()
        if received_time_data_from_usb:
            deadline_fields, deadline_ticks = received_time_data_from_usb
            (year, month, day, hour, minute, second, wday, yday) = deadline_fields
            while ticks_diff(deadline_ticks, supervisor.ticks_ms()) > 0:
                await asyncio.sleep(0.001 / 2)  # *ticks_diff(deadline, time.ticks_ms())
            time_to_set = time.struct_time((year, month, day, hour, minute, second, wday, yday, 0))
            batteryRTC.datetime = time_to_set
            ticks_ms_for_written_instant = supervisor.ticks_ms()
            write_relative_to_deadline = adafruit_ticks.ticks_diff(deadline_ticks, ticks_ms_for_written_instant)
            print(f'write_relative_to_deadline: {write_relative_to_deadline}')

            print(f'time_to_set        : {time_to_set}')
            print(f'batteryRTC.datetime: {batteryRTC.datetime}')
            set_rp2040_rtc_from_battery_rtc()

        await asyncio.sleep(0.001 / 2)


def readDeadlineAndTimeToDeadlineFromUSB():
    ch, buffer = '', ''
    ticks_ms_for_read_instant = supervisor.ticks_ms()
    while stdin in select([stdin], [], [], 0)[0]:
        ch = stdin.read(1)
        buffer = buffer + ch
    if buffer:
        print("Received USB data!")
        for i in range(len(buffer)):
            if buffer[i] == 'T':
                break
        buffer = buffer[i:]
        if buffer[:1] == 'T' and buffer[-1] == '_':
            buffData = buffer[1:-1]
            print(f'buffData: {buffData}')
            buffFields = [int(x) for x in buffData.split(',')]
            deadLineFields = buffFields[:-1]
            deadLineFields.append(0)
            timeToDeadLine = buffFields[-1]
            print("timeToDeadLine:", end='');
            print(timeToDeadLine)
            return deadLineFields, adafruit_ticks.ticks_add(ticks_ms_for_read_instant, timeToDeadLine)
