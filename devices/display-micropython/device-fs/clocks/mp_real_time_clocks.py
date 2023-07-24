import machine

from machine import SoftI2C, Pin

from clocks.synchro import RealTimeClock
from ds3231_gen import *

rp2040_rtc = machine.RTC()
rtc_i2c = SoftI2C(scl=Pin(7), sda=Pin(6), freq=100000)
ds3231_rtc = DS3231(rtc_i2c)

print(f"ds3231={ds3231_rtc.get_time()}")
print(f"rp2040={rp2040_rtc.datetime()}")


def set_rp2040_rtc_from_battery_rtc():
    for x in range(2):
        initial_battery_rtc_time = ds3231_rtc.get_time()
        latest_battery_rtc_time = initial_battery_rtc_time
        while latest_battery_rtc_time == initial_battery_rtc_time:
            latest_battery_rtc_time = ds3231_rtc.get_time()

    rp2040_rtc.datetime(latest_battery_rtc_time)
    print(f'latest_battery_rtc_time: {latest_battery_rtc_time}')
    print(f'rp2040_rtc.datetime: {rp2040_rtc.datetime()}')


class MicroPythonClock(RealTimeClock):
    def ymd_hms_tuple_for_repr(self, t):
        # https://docs.micropython.org/en/v1.20.0/library/pyb.RTC.html?highlight=rtc#pyb.RTC.datetime
        year, month, day, weekday, hours, minutes, seconds, subseconds = t
        return year, month, day, hours, minutes, seconds

external_clock = MicroPythonClock("ds3231", lambda: ds3231_rtc.get_time(), lambda rep: (ds3231_rtc.set_time(rep)))
internal_clock = MicroPythonClock("rp2040", lambda: rp2040_rtc.datetime(), lambda rep: (rp2040_rtc.datetime(rep)))

all_clocks = [internal_clock, external_clock]

set_rp2040_rtc_from_battery_rtc()
