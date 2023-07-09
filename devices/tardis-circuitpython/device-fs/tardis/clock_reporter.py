import asyncio

from adafruit_ticks import *
import time
import rtc
import board
import adafruit_ds3231  # battery-backed RTC

rp2040_rtc = rtc.RTC()

batteryRTC = adafruit_ds3231.DS3231(board.I2C())


class ClockSecondTransition:
    def __init__(self, start_tick_ms: int, size_tick_ms: int):
        self.start_tick_ms = start_tick_ms
        self.size_tick_ms = size_tick_ms
        self.end_tick_ms = (start_tick_ms + size_tick_ms) % 1000

    def summary(self) -> str:
        return f'[{self.start_tick_ms} - {self.end_tick_ms}](size: {self.size_tick_ms})'


class ClockReporter:
    timestamp_format = "%04d-%02d-%02dT%02d:%02d:%02dZ"

    def __init__(self, name: int, get_time):
        self.name = name
        self.get_time = get_time

    def sleep_and_read_clock(self, ticks_ms_to_sleep: int) -> (int, time.struct_time):  #
        adjusted_ticks_to_sleep = ticks_ms_to_sleep - 2  # typical overshoot
        if adjusted_ticks_to_sleep > 0:
            # await asyncio.sleep(ticks_ms_to_sleep / 1000)
            time.sleep(adjusted_ticks_to_sleep / 1000)
        before_read = ticks_ms()
        read_time = self.get_time()
        after_read = ticks_ms()
        # print(f'ticks to read={ticks_diff(after_read, before_read)}')
        return before_read, read_time

    def sleep_to_tick_ms_target(self, tick_ms_target: int):
        ticks_prior_to_sleep = ticks_ms()
        ticks_to_sleep = ticks_diff(tick_ms_target, ticks_prior_to_sleep)
        #print(f'ticks_to_sleep={ticks_to_sleep}')
        ticks_on_wake, time_on_wake = self.sleep_and_read_clock(ticks_to_sleep)
        # print(f'ticks_prior_to_sleep={ticks_prior_to_sleep % 1000} ticks_on_wake={ticks_on_wake % 1000} overshoot={ticks_diff(ticks_on_wake, tick_ms_target)}')
        return ticks_on_wake, time_on_wake

    def start(self):
        confirmed_range = ClockSecondTransition(0, 1000)
        range_divider = 2
        last_clock_report_ticks_ms = 0
        desired_range_size_ticks_ms = 20
        desired_report_period_ticks_seconds: int = 10
        desired_report_period_ticks_ms = desired_report_period_ticks_seconds * 1000  # shd be a whole number of seconds

        while True:
            current_ticks = ticks_ms()
            ticks_to_range_start = (1000 + confirmed_range.start_tick_ms - (current_ticks % 1000)) % 1000
            # print(f'\nticks_to_range_start={ticks_to_range_start}')
            target_range_start_ticks = ticks_add(current_ticks, ticks_to_range_start)
            target_range_end_ticks = ticks_add(target_range_start_ticks, confirmed_range.size_tick_ms)

            start_ticks, start_time = self.sleep_to_tick_ms_target(target_range_start_ticks)

            samples_left_for_range = range_divider if confirmed_range.size_tick_ms > desired_range_size_ticks_ms else 1
            # print(f'start_ticks={start_ticks}')
            prior_ticks = start_ticks

            # start loop here?
            while samples_left_for_range > 0:  # we are going to scan the 'confirmed range' for this second
                boo = ticks_ms()
                ticks_until_end_of_confirmed_range = ticks_diff(target_range_end_ticks, boo)
                leg_target_ticks = ticks_add(boo, round(ticks_until_end_of_confirmed_range / samples_left_for_range))
                print(f'samples_left_for_range={samples_left_for_range} confirmed_range_size_tick_ms={confirmed_range.size_tick_ms} ticks_until_end_of_confirmed_range={ticks_until_end_of_confirmed_range} leg_target_ticks={leg_target_ticks}')

                samples_left_for_range -= 1
                leg_ticks, leg_time = self.sleep_to_tick_ms_target(leg_target_ticks)
                if leg_time != start_time:  # transition!
                    confirmed_range = ClockSecondTransition(
                        prior_ticks % 1000,
                        min(ticks_diff(leg_ticks, prior_ticks), 1000)
                    )
                    print(f'Transition on {confirmed_range.summary()}!')

                    samples_left_for_range = 0  # next time we run, we want to be slicing up the new range

                    if confirmed_range.size_tick_ms <= desired_range_size_ticks_ms:  # we're accurate!
                        if ticks_diff(leg_ticks, last_clock_report_ticks_ms) > desired_report_period_ticks_ms:
                            t = leg_time
                            timestamp = ClockReporter.timestamp_format % (
                                t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
                            print(f'clock_report:{self.name}={timestamp}')
                            last_clock_report_ticks_ms = leg_ticks
                        next_report_desired_ticks_ms = ticks_add(last_clock_report_ticks_ms,
                                                                 desired_report_period_ticks_ms)
                        self.sleep_to_tick_ms_target(next_report_desired_ticks_ms)
                else:  # no transition!
                    ticks_to_range_end = ticks_diff(target_range_end_ticks, leg_ticks)
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


battery_rtc_reporter = ClockReporter("ds3231", lambda: batteryRTC.datetime)
