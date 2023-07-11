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

# async def clock_reporters():
#     await asyncio.gather(
#         asyncio.create_task(clock_reporter("ds3231", lambda: batteryRTC.datetime))
#     )
#
#
# async def clock_reporter(name: str, get_time):
#     def sleep_and_read_clock(ticks_ms_to_sleep: int):  # -> (int, time.struct_time)
#         if ticks_ms_to_sleep > 0:
#             # await asyncio.sleep(ticks_ms_to_sleep / 1000)
#             time.sleep(ticks_ms_to_sleep / 1000)
#         return (ticks_ms(), get_time())
#
#     def sleep_to_tick_ms_target(current_ticks: int, tick_ms_target: int):
#         ticks_to_sleep = ticks_diff(tick_ms_target, current_ticks)
#         print(f'ticks_to_sleep={ticks_to_sleep}')
#         boop, beep = sleep_and_read_clock(ticks_to_sleep)
#         return boop, beep
#
#     confirmed_range_start_tick_ms = 0
#     confirmed_range_size_tick_ms = 1000
#     range_divider = 2
#     last_clock_report_ticks_ms = 0
#     desired_range_size_ticks_ms = 20
#     desired_report_period_ticks_seconds: int = 10
#     desired_report_period_ticks_ms = desired_report_period_ticks_seconds * 1000  # should be a whole number of seconds
#     timestamp_format = "%04d-%02d-%02dT%02d:%02d:%02dZ"
#
#     while True:
#         current_ticks = ticks_ms()
#         ticks_to_range_start = (1000 + confirmed_range_start_tick_ms - (current_ticks % 1000)) % 1000
#         print(f'ticks_to_range_start={ticks_to_range_start}')
#         target_range_start_ticks = ticks_add(current_ticks, ticks_to_range_start)
#         target_range_end_ticks = ticks_add(target_range_start_ticks, confirmed_range_size_tick_ms)
#
#         target = sleep_to_tick_ms_target(current_ticks, target_range_start_ticks)
#         print(target)
#         start_ticks, start_time = target
#         samples_left_for_range = range_divider if confirmed_range_size_tick_ms > desired_range_size_ticks_ms else 1
#         print(f'samples_left_for_range={samples_left_for_range}')
#         prior_ticks = start_ticks
#
#         # start loop here?
#         while samples_left_for_range > 0:  # we are going to scan the 'confirmed range' for this second
#             print(f'confirmed_range_size_tick_ms={confirmed_range_size_tick_ms}')
#             ticks_ms_to_sleep = round(ticks_diff(target_range_end_ticks,prior_ticks) / samples_left_for_range)
#             samples_left_for_range -= 1
#             leg_ticks, leg_time = sleep_and_read_clock(ticks_ms_to_sleep)
#             if leg_time != start_time:  # transition!
#                 confirmed_range_start_tick_ms = prior_ticks % 1000
#                 confirmed_range_size_tick_ms = min(ticks_diff(leg_ticks, prior_ticks), 1000)
#
#                 samples_left_for_range = 0  # next time we run, we want to be slicing up the new range
#
#                 if confirmed_range_size_tick_ms <= desired_range_size_ticks_ms:  # we're accurate!
#                     if ticks_diff(leg_ticks, last_clock_report_ticks_ms) > desired_report_period_ticks_ms:
#                         t = leg_time
#                         timestamp = timestamp_format % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
#                         print(f'clock_report:{name}={timestamp}')
#                         last_clock_report_ticks_ms = leg_ticks
#                     next_report_desired_ticks_ms = ticks_add(last_clock_report_ticks_ms, desired_report_period_ticks_ms)
#                     sleep_to_tick_ms_target(next_report_desired_ticks_ms)
#             else:  # no transition!
#                 ticks_to_range_end = ticks_diff(leg_ticks, target_range_end_ticks)
#                 if ticks_to_range_end <= 0:  # we've checked to the end of the confirmed range! It must be wrong!
#                     confirmed_range_start_tick_ms = leg_ticks  # we know that the transition must come after...
#                     confirmed_range_size_tick_ms = max(1000 - ticks_diff(leg_ticks, start_ticks), 1)
#                     samples_left_for_range = 0
#                 else:
#                     samples_left_for_range -= 1  # We want to check the next segment of the range...


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
