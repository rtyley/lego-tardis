import asyncio

from adafruit_ticks import *
import time
import rtc
import board
import adafruit_ds3231  # battery-backed RTC
from math import ceil

rp2040_rtc = rtc.RTC()

batteryRTC = adafruit_ds3231.DS3231(board.I2C())


class ClockSecondTransition:
    def __init__(self, start_tick_ms: int, size_tick_ms: int):
        self.start_tick_ms = start_tick_ms
        self.size_tick_ms = size_tick_ms
        self.end_tick_ms = (start_tick_ms + size_tick_ms) % 1000

    def summary(self) -> str:
        return f'[{self.start_tick_ms} - {self.end_tick_ms}](size: {self.size_tick_ms})'


class Clock(object):
    timestamp_format = "%04d-%02d-%02dT%02d:%02d:%02dZ"

    def __init__(self, name: str, get_time_repr):
        self.name = name
        self.get_time_repr = get_time_repr

    def ymd_hms_tuple_for_repr(self, t):
        raise NotImplementedError("Please Implement this method")

    def timestamp_for_repr(self, repr):
        return Clock.timestamp_for(self.ymd_hms_tuple_for_repr(repr))

    @staticmethod
    def timestamp_for(ymd_hms_tuple: (int, int, int, int, int, int)):
        return Clock.timestamp_format % ymd_hms_tuple


class CircuitpythonClock(Clock):
    def ymd_hms_tuple_for_repr(self, t):
        return t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec


class ClockReporter:
    timestamp_format = "%04d-%02d-%02dT%02d:%02d:%02dZ"

    def __init__(self, clock: Clock):
        self.clock = clock

    @staticmethod
    def nextTargetIntervalGiven(current_ticks, confirmed_range):
        ticks_to_range_start = (1000 + confirmed_range.start_tick_ms - (current_ticks % 1000)) % 1000
        # print(f'\nticks_to_range_start={ticks_to_range_start}')
        target_range_start_ticks = ticks_add(current_ticks, ticks_to_range_start)
        target_range_end_ticks = ticks_add(target_range_start_ticks, confirmed_range.size_tick_ms)
        return target_range_start_ticks, target_range_end_ticks

    @staticmethod
    def leg_target_start_ticks(samples_left_for_range, target_end_ticks):
        current_ticks = ticks_ms()
        ticks_until_end_of_confirmed_range = ticks_diff(target_end_ticks, current_ticks)
        return ticks_add(current_ticks, round(ticks_until_end_of_confirmed_range / samples_left_for_range))

    async def sleep_to_tick_ms_target(self, tick_ms_target: int) -> (int, time.struct_time):
        def state() -> (int, int):
            ticks = ticks_ms()
            return ticks, ticks_diff(tick_ms_target, ticks)

        current_ticks, ticks_to_sleep = state()
        while ticks_to_sleep > 0:
            adjusted_ticks_to_sleep = ticks_to_sleep - 1  # try to avoid overshoot
            # time.sleep(adjusted_ticks_to_sleep / 1000)
            await asyncio.sleep(adjusted_ticks_to_sleep / 1000)
            current_ticks, ticks_to_sleep = state()
        return current_ticks, self.clock.get_time_repr()

    async def start(self):
        confirmed_range = ClockSecondTransition(0, 1000)
        max_samples_per_second = 5
        last_clock_report_ticks_ms = 0
        desired_range_size_ticks_ms = 10
        desired_report_period_ticks_seconds: int = 10
        desired_report_period_ticks_ms = desired_report_period_ticks_seconds * 1000  # shd be a whole number of seconds
        while True:
            target_start_ticks, target_end_ticks = ClockReporter.nextTargetIntervalGiven(ticks_ms(), confirmed_range)

            start_ticks, start_time = await self.sleep_to_tick_ms_target(target_start_ticks)

            samples_left_for_range = \
                max(min(ceil(confirmed_range.size_tick_ms / desired_range_size_ticks_ms), max_samples_per_second), 1)
            # print(f'\nstart_ticks={start_ticks}')
            prior_ticks = start_ticks

            # start loop here?
            while samples_left_for_range > 0:  # we are going to scan the 'confirmed range' for this second
                leg_target_ticks = ClockReporter.leg_target_start_ticks(samples_left_for_range, target_end_ticks)

                samples_left_for_range -= 1
                leg_ticks, leg_time = await self.sleep_to_tick_ms_target(leg_target_ticks)
                if leg_time != start_time:  # transition!
                    samples_left_for_range = 0  # next time we run, we want to be slicing up a range on a new second
                    old_confirmed_range_was_broad = confirmed_range.size_tick_ms > desired_range_size_ticks_ms
                    confirmed_range = ClockSecondTransition(
                        prior_ticks % 1000,
                        min(ticks_diff(leg_ticks, prior_ticks), 1000)
                    )
                    # print(f'Transition on {confirmed_range.summary()}!')

                    if confirmed_range.size_tick_ms <= desired_range_size_ticks_ms:  # we're accurate!
                        if old_confirmed_range_was_broad or \
                                ticks_diff(leg_ticks, last_clock_report_ticks_ms) > desired_report_period_ticks_ms:
                            print(f'clock_report:{self.clock.name}={self.clock.timestamp_for_repr(leg_time)}')
                            if old_confirmed_range_was_broad:
                                print(f'Converged on new range: {confirmed_range.summary()}')
                            last_clock_report_ticks_ms = leg_ticks

                        next_report_desired_ticks_ms = ticks_add(prior_ticks,
                                                                 desired_report_period_ticks_ms)
                        await self.sleep_to_tick_ms_target(next_report_desired_ticks_ms)
                else:  # no transition!
                    ticks_to_range_end = ticks_diff(target_end_ticks, leg_ticks)
                    # print(f'ticks_to_range_end={ticks_to_range_end}')
                    if ticks_to_range_end <= 0:  # we've checked to the end of the confirmed range! It must be wrong!
                        ticks_checked = ticks_diff(leg_ticks, start_ticks)
                        print(f'Range {confirmed_range.summary()} was wrong! ticks_checked={ticks_checked}')
                        confirmed_range = ClockSecondTransition(
                            leg_ticks % 1000,  # we know that the transition must come after...
                            max(1000 - ticks_checked, 1)
                        )
                        samples_left_for_range = 0
                    else:
                        prior_ticks = leg_ticks


internal_clock = CircuitpythonClock("ds3231", lambda: batteryRTC.datetime)
external_clock = CircuitpythonClock("rp2040", lambda: rp2040_rtc.datetime)

all_clocks = [internal_clock, external_clock]
