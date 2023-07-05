import asyncio

import adafruit_ticks
import board
import adafruit_ds3231  # battery-backed RTC
import supervisor
import time
from sys import stdin
from select import select
from tardis.windows import set_all_windows
from adafruit_ticks import ticks_diff
import rtc
import time

rp2040_rtc = rtc.RTC()

i2c = board.I2C()
batteryRTC = adafruit_ds3231.DS3231(i2c)

t = batteryRTC.datetime
print(t)  # uncomment for debugging


def clock_check(expensive_clock: bool) -> time.struct_time:
    t = batteryRTC.datetime if expensive_clock else rp2040_rtc.datetime
    name = "ds3231" if expensive_clock else "rp2040"
    timestamp = "%04d-%02d-%02dT%02d:%02d:%02dZ" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    print(f'clock_check:{name}={timestamp}')
    return t


# def parse()
#     # upcoming-clock:2020-03-20T14:28:23Z,345ms
#     altMSG = f'upcoming-clock:{t.isoformat()}Z,{millisToWaitForDeadline}ms'


def set_rp2040_rtc_from_battery_rtc():
    initial_battery_rtc_time = batteryRTC.datetime
    latest_battery_rtc_time = initial_battery_rtc_time
    while latest_battery_rtc_time == initial_battery_rtc_time:
        latest_battery_rtc_time = batteryRTC.datetime
    rp2040_rtc.datetime = latest_battery_rtc_time
    print(f'latest_battery_rtc_time: {latest_battery_rtc_time}')

async def watch_clock():
    last_battery_rtc = batteryRTC.datetime
    last_rp2040_rtc = rp2040_rtc.datetime
    print("Waiting for time signal....")
    while True:
        now_rp2040_rtc = rp2040_rtc.datetime
        now_battery_rtc = batteryRTC.datetime
        if now_rp2040_rtc.tm_sec % 5 == 0 and now_rp2040_rtc != last_rp2040_rtc:
            last_rp2040_rtc = clock_check(False)
        if now_battery_rtc.tm_sec % 5 == 0 and now_battery_rtc != last_battery_rtc:
            last_battery_rtc = clock_check(True)


        now_ticks = supervisor.ticks_ms()
        # if now_rtc.tm_sec != last_rtc.tm_sec:
        #     last_rtc = now_rtc
        #     ticks_offset = now_ticks % 1000
        #     # print(ticks_offset)
        #     if now_rtc.tm_sec % 10 == 0:
        #         clock_check(True)
        #         clock_check(False)
        #         print('RTC :', end='');
        #         print(now_rtc)
        #         if ticks_offset > 0:
        #             while (supervisor.ticks_ms() + 4) % 1000 >= ticks_offset:
        #                 await asyncio.sleep(0.0001)
        #             batteryRTC.datetime = now_rtc

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
            set_all_windows(timeToDeadLine // 4)
            return deadLineFields, adafruit_ticks.ticks_add(ticks_ms_for_read_instant, timeToDeadLine)
