import rtc
import board
import adafruit_ds3231  # battery-backed RTC

from synchro import RealTimeClock

rp2040_rtc = rtc.RTC()
batteryRTC = adafruit_ds3231.DS3231(board.I2C())


class CircuitPythonClock(RealTimeClock):
    def ymd_hms_tuple_for_repr(self, t):
        # https://docs.circuitpython.org/en/latest/shared-bindings/time/index.html#time.struct_time
        return t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec


external_clock = CircuitPythonClock("ds3231", lambda: batteryRTC.datetime)
internal_clock = CircuitPythonClock("rp2040", lambda: rp2040_rtc.datetime)

all_clocks = [external_clock]  # [internal_clock, external_clock]
