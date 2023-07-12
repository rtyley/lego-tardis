import machine

from synchro import RealTimeClock
from machine import SoftI2C
from ds3231_gen import *

rp2040_rtc = machine.RTC()
rtc_i2c = SoftI2C(scl=Pin(7), sda=Pin(6), freq=100000)
ds3231_rtc = DS3231(rtc_i2c)

class MicroPythonClock(RealTimeClock):
    def ymd_hms_tuple_for_repr(self, t):
        return t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec


external_clock = MicroPythonClock("ds3231", lambda: batteryRTC.datetime)
internal_clock = MicroPythonClock("rp2040", lambda: rp2040_rtc.datetime)

all_clocks = [external_clock]  # [internal_clock, external_clock]
