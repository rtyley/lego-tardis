import time
from machine import Pin
from utime import time, localtime, sleep
from time import ticks_diff, ticks_add, ticks_ms, sleep_us, gmtime
from select import select
from sys import stdin
from machine import SoftI2C

from clocks.mp_real_time_clocks import all_clocks
from clocks.synchro import ClockReporter
from secrets import treasurePassphrases

from machine import Pin, Timer
import time
from ds3231_gen import *
import uasyncio as asyncio




print("The family together")


async def bar(x):
    count = 0
    while True:
        count += 1
        print('Instance: {} count: {}'.format(x, count))
        await asyncio.sleep(1)  # Pause 1s


async def main():
    for c in all_clocks:
        asyncio.create_task(ClockReporter(c).start())
    while True:
        await asyncio.sleep(10)


asyncio.run(main())


print("Loom stick!")


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


class Scheduler:
    class Schedule:
        def __init__(self, name, duration, callback):
            self.name = name
            self.duration = duration
            self.callback = callback
            self.lastrun = time.ticks_ms()

    count = 0

    def __init__(self):
        self.schedules = []

    def start(self):
        self.start = time.ticks_ms()
        self.timer = Timer(period=1, callback=self.event_callback)

    def schedule(self, name, duration, callback):
        self.schedules.append(self.Schedule(name, duration, callback))

    def event_callback(self, t):
        for schedule in self.schedules:
            if schedule.duration == 1:
                schedule.callback(t)
            else:
                tm = time.ticks_ms()
                if time.ticks_diff(tm, schedule.lastrun) > schedule.duration:
                    schedule.callback(t)
                    schedule.lastrun = tm


@singleton
class Display:
    def __init__(self, scheduler):
        self.a0 = Pin(16, Pin.OUT)
        self.a1 = Pin(18, Pin.OUT)
        self.a2 = Pin(22, Pin.OUT)

        self.sdi = Pin(11, Pin.OUT)
        self.clk = Pin(10, Pin.OUT)
        self.le = Pin(12, Pin.OUT)

        self.row = 0
        self.count = 0
        self.leds = [[0] * 32 for i in range(0, 8)]
        self.leds_changed = False
        self.disp_offset = 2
        self.initialise_fonts()
        self.initialise_icons()
        scheduler.schedule("enable-leds", 1, self.enable_leds)

    def enable_leds(self, t):
        self.count += 1
        self.row = (self.row + 1) % 8
        led_row = self.leds[self.row]
        if True:
            for col in range(32):
                self.clk.value(0)
                self.sdi.value(led_row[col])
                self.clk.value(1)
            self.le.value(1)
            self.le.value(0)
            self.leds_changed = False

        self.a0.value(1 if self.row & 0x01 else 0)
        self.a1.value(1 if self.row & 0x02 else 0)
        self.a2.value(1 if self.row & 0x04 else 0)

    def clear(self, x=0, y=0, w=24, h=7):
        for yy in range(y, y + h + 1):
            for xx in range(x, x + w + 1):
                self.leds[yy][xx] = 0

    def show_char(self, character, pos):
        pos += self.disp_offset  # Plus the offset of the status indicator
        char = self.ziku[character]
        for row in range(1, 8):
            byte = char.rows[row - 1]
            for col in range(0, char.width):
                self.leds[row][pos + col] = (byte >> col) % 2
        self.leds_changed = True

    def show_text(self, text, pos=0):
        i = 0
        while i < len(text):
            if text[i:i + 2] in self.ziku:
                c = text[i:i + 2]
                i += 2
            else:
                c = text[i]
                i += 1
            char = self.ziku[c]
            self.show_char(c, pos)
            width = self.ziku[c].width
            pos += width + 1

    def show_icon(self, name):
        icon = self.Icons[name]
        for w in range(icon.width):
            self.leds[icon.y][icon.x + w] = 1
        self.leds_changed = True

    def hide_icon(self, name):
        icon = self.Icons[name]
        for w in range(icon.width):
            self.leds[icon.y][icon.x + w] = 0
        self.leds_changed = True

    def backlight_on(self):
        self.leds[0][2] = 1
        self.leds[0][5] = 1

    def backlight_off(self):
        self.leds[0][2] = 0
        self.leds[0][5] = 0

    def print(self):
        for row in range(0, 8):
            for pos in range(0, 24):
                print("X" if self.leds[row][pos] == 1 else " ", end="")
            print("")

    def square(self):
        '''
        Prints a crossed square. For debugging purposes.
        '''
        for row in range(1, 8):
            self.leds[row][2] = 1
            self.leds[row][23] = 1
        for col in range(2, 23):
            self.leds[1][col] = 1
            self.leds[7][col] = 1
            self.leds[int(col / 24 * 7) + 1][col] = 1
            self.leds[7 - int(col / 24 * 7)][col] = 1

    class Character:
        def __init__(self, width, rows, offset=2):
            self.width = width
            self.rows = rows
            self.offset = offset

    class Icon:
        def __init__(self, x, y, width=1):
            self.x = x
            self.y = y
            self.width = width

    def initialise_icons(self):
        self.Icons = {
            "MoveOn": self.Icon(0, 0, width=2),
            "AlarmOn": self.Icon(0, 1, width=2),
            "CountDown": self.Icon(0, 2, width=2),
            "°F": self.Icon(0, 3),
            "°C": self.Icon(1, 3),
            "AM": self.Icon(0, 4),
            "PM": self.Icon(1, 4),
            "CountUp": self.Icon(0, 5, width=2),
            "Hourly": self.Icon(0, 6, width=2),
            "AutoLight": self.Icon(0, 7, width=2),
            "Mon": self.Icon(3, 0, width=2),
            "Tue": self.Icon(6, 0, width=2),
            "Wed": self.Icon(9, 0, width=2),
            "Thur": self.Icon(12, 0, width=2),
            "Fri": self.Icon(15, 0, width=2),
            "Sat": self.Icon(18, 0, width=2),
            "Sun": self.Icon(21, 0, width=2),
        }

    day_of_week = {
        0: "Sun",
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thur",
        5: "Fri",
        6: "Sat"
    }

    def show_day(self, int):
        self.clear()
        self.show_icon(self.day_of_week[int])

    # Derived from c code created by yufu on 2021/1/23.
    # Modulus method: negative code, reverse, line by line, 4X7 font
    def initialise_fonts(self):
        self.ziku = {
            "all": self.Character(width=3, rows=[0x05, 0x05, 0x03, 0x03, 0x03, 0x03, 0x03]),
            "0": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x09, 0x09, 0x09, 0x06]),
            "1": self.Character(width=4, rows=[0x04, 0x06, 0x04, 0x04, 0x04, 0x04, 0x0E]),
            "2": self.Character(width=4, rows=[0x06, 0x09, 0x08, 0x04, 0x02, 0x01, 0x0F]),
            "3": self.Character(width=4, rows=[0x06, 0x09, 0x08, 0x06, 0x08, 0x09, 0x06]),
            "4": self.Character(width=4, rows=[0x08, 0x0C, 0x0A, 0x09, 0x0F, 0x08, 0x08]),
            "5": self.Character(width=4, rows=[0x0F, 0x01, 0x07, 0x08, 0x08, 0x09, 0x06]),
            "6": self.Character(width=4, rows=[0x04, 0x02, 0x01, 0x07, 0x09, 0x09, 0x06]),
            "7": self.Character(width=4, rows=[0x0F, 0x09, 0x04, 0x04, 0x04, 0x04, 0x04]),
            "8": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x06, 0x09, 0x09, 0x06]),
            "9": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x0E, 0x08, 0x04, 0x02]),
            "A": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x0F, 0x09, 0x09, 0x09]),
            "B": self.Character(width=4, rows=[0x07, 0x09, 0x09, 0x07, 0x09, 0x09, 0x07]),
            "C": self.Character(width=4, rows=[0x06, 0x09, 0x01, 0x01, 0x01, 0x09, 0x06]),
            "D": self.Character(width=4, rows=[0x07, 0x09, 0x09, 0x09, 0x09, 0x09, 0x07]),
            "E": self.Character(width=4, rows=[0x0F, 0x01, 0x01, 0x0F, 0x01, 0x01, 0x0F]),
            "F": self.Character(width=4, rows=[0x0F, 0x01, 0x01, 0x0F, 0x01, 0x01, 0x01]),
            "G": self.Character(width=4, rows=[0x06, 0x09, 0x01, 0x0D, 0x09, 0x09, 0x06]),
            "H": self.Character(width=4, rows=[0x09, 0x09, 0x09, 0x0F, 0x09, 0x09, 0x09]),
            "I": self.Character(width=3, rows=[0x07, 0x02, 0x02, 0x02, 0x02, 0x02, 0x07]),
            "J": self.Character(width=4, rows=[0x0F, 0x08, 0x08, 0x08, 0x09, 0x09, 0x06]),
            "K": self.Character(width=4, rows=[0x09, 0x05, 0x03, 0x01, 0x03, 0x05, 0x09]),
            "L": self.Character(width=4, rows=[0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x0F]),
            "M": self.Character(width=5, rows=[0x11, 0x1B, 0x15, 0x11, 0x11, 0x11, 0x11]),  # 5×7
            "N": self.Character(width=4, rows=[0x09, 0x09, 0x0B, 0x0D, 0x09, 0x09, 0x09]),
            "O": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x09, 0x09, 0x09, 0x06]),
            "P": self.Character(width=4, rows=[0x07, 0x09, 0x09, 0x07, 0x01, 0x01, 0x01]),
            "Q": self.Character(width=5, rows=[0x0E, 0x11, 0x11, 0x11, 0x15, 0x19, 0x0E]),  # Q
            "R": self.Character(width=4, rows=[0x07, 0x09, 0x09, 0x07, 0x03, 0x05, 0x09]),  # R
            "S": self.Character(width=4, rows=[0x06, 0x09, 0x02, 0x04, 0x08, 0x09, 0x06]),  # S
            "T": self.Character(width=5, rows=[0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04]),  # 5×7
            "U": self.Character(width=4, rows=[0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x06]),
            "V": self.Character(width=5, rows=[0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04]),  # 5×7
            "W": self.Character(width=5, rows=[0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11]),  # 5×7
            "X": self.Character(width=5, rows=[0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11]),  # 5*7
            "Y": self.Character(width=5, rows=[0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04]),  # 5*7
            "Z": self.Character(width=4, rows=[0x0F, 0x08, 0x04, 0x02, 0x01, 0x0F, 0x00]),  # 4×7

            ":": self.Character(width=2, rows=[0x00, 0x03, 0x03, 0x00, 0x03, 0x03, 0x00]),  # 2×7
            " :": self.Character(width=2, rows=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # colon width space
            "°C": self.Character(width=4, rows=[0x01, 0x0C, 0x12, 0x02, 0x02, 0x12, 0x0C]),  # celcuis 5×7
            "°F": self.Character(width=4, rows=[0x01, 0x1E, 0x02, 0x1E, 0x02, 0x02, 0x02]),  # farenheit
            " ": self.Character(width=4, rows=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # space

            ".": self.Character(width=1, rows=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]),  # 1×7
            "-": self.Character(width=2, rows=[0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00]),  # 2×7

            "/": self.Character(width=2, rows=[0x02, 0x02, 0x02, 0x01, 0x01, 0x01, 0x01, 0x01]),  # 3×7
            "°C2": self.Character(width=4, rows=[0x00, 0x01, 0x0C, 0x12, 0x02, 0x02, 0x12, 0x0C]),  # 5×7
            "°F2": self.Character(width=4, rows=[0x00, 0x01, 0x1E, 0x02, 0x1E, 0x02, 0x02, 0x02]),

        }
        self.digital_tube = {
            "0": [0x0F, 0x09, 0x09, 0x09, 0x09, 0x09, 0x0F],
            "1": [0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08],
            "2": [0x0F, 0x08, 0x08, 0x0F, 0x01, 0x01, 0x0F],
            "3": [0x0F, 0x08, 0x08, 0x0F, 0x08, 0x08, 0x0F],
            "4": [0x09, 0x09, 0x09, 0x0F, 0x08, 0x08, 0x08],
            "5": [0x0F, 0x01, 0x01, 0x0F, 0x08, 0x08, 0x0F],
            "5": [0x0F, 0x01, 0x01, 0x0F, 0x09, 0x09, 0x0F],
            "6": [0x0F, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08],
            "7": [0x0F, 0x09, 0x09, 0x0F, 0x09, 0x09, 0x0F],
            "8": [0x0F, 0x09, 0x09, 0x0F, 0x08, 0x08, 0x0F],
            "A": [0x0F, 0x09, 0x09, 0x0F, 0x09, 0x09, 0x09],
            "B": [0x01, 0x01, 0x01, 0x0F, 0x09, 0x09, 0x0F],
            "C": [0x0F, 0x01, 0x01, 0x01, 0x01, 0x01, 0x0F],
            "D": [0x08, 0x08, 0x08, 0x0F, 0x09, 0x09, 0x0F],
            "E": [0x0F, 0x01, 0x01, 0x0F, 0x01, 0x01, 0x0F],
            "F": [0x0F, 0x01, 0x01, 0x0F, 0x01, 0x01, 0x01],
            "H": [0x09, 0x09, 0x09, 0x0F, 0x09, 0x09, 0x09],
            "L": [0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x0F],
            "N": [0x0F, 0x09, 0x09, 0x09, 0x09, 0x09, 0x09],
            "P": [0x0F, 0x09, 0x09, 0x0F, 0x01, 0x01, 0x01],
            "U": [0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x0F],
            ":": [0x00, 0x03, 0x03, 0x00, 0x03, 0x03, 0x00],  # 2×7
            "°C": [0x01, 0x1E, 0x02, 0x02, 0x02, 0x02, 0x1E],  # celcius 5×7
            "°F": [0x01, 0x1E, 0x02, 0x1E, 0x02, 0x02, 0x02],  # farenheit
            " ": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "T": [0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04],  # 5*7
            ".": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01],  # 2×7
            "-": [0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00],  # 2×7
            "M": [0x00, 0x11, 0x1B, 0x15, 0x11, 0x11, 0x11, 0x11],  # 5×7
            "/": [0x00, 0x04, 0x04, 0x02, 0x02, 0x02, 0x01, 0x01],  # 3×7
            "°C2": [0x00, 0x01, 0x0C, 0x12, 0x02, 0x02, 0x12, 0x0C],  # celcuis 5x7
            "°F2": [0x00, 0x01, 0x1E, 0x02, 0x1E, 0x02, 0x02, 0x02],  # farenheit
            "V": [0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1F],  # 5×7
            "W": [0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11],  # 5×7
        }


scheduler = Scheduler()
display = Display(scheduler)
scheduler.start()

led_onboard = Pin(25, Pin.OUT)
led_onboard.toggle()

display.show_text("GOOD")


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


# Write your code here :-)
rp2040_rtc = machine.RTC()
rtc_i2c = SoftI2C(scl=Pin(7), sda=Pin(6), freq=100000)
ds3231_rtc = DS3231(rtc_i2c)

print(rp2040_rtc.datetime())
print(ds3231_rtc.get_time())


# (2022, 3, 9,  3, 20, 52, 30, 0)
# (1922, 3, 9, 20, 52,  7,  2, 0)

def readDeadlineAndTimeToDeadlineFromUSB():
    ch, buffer = '', ''
    ticks_ms_for_read_instant = ticks_ms()
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
            buffFields = [int(x) for x in buffData.split(',')]
            deadLineFields = buffFields[:-1]
            deadLineFields.append(0)
            timeToDeadLine = buffFields[-1]
            print("timeToDeadLine:", end='');
            print(timeToDeadLine)
            return deadLineFields, ticks_add(ticks_ms_for_read_instant, timeToDeadLine)


led_onboard = Pin(25, Pin.OUT)

rp2040_rtc = machine.RTC()
lastSecondPrinted = rp2040_rtc.datetime()[6]

displayed_text = None


# def ticks_for_next_10_second_rollover(last_ds3231Time, ticks_at_transition):

def set_pico_rtc_from_ds3231():
    initial_ds3231_seconds = ds3231_rtc.get_time()[5]
    latest_ds3231_time = ds3231_rtc.get_time()
    ticks_for_transition = ticks_ms()
    while latest_ds3231_time[5] is initial_ds3231_seconds:
        ticks_for_transition = ticks_ms() % 1000
        latest_ds3231_time = ds3231_rtc.get_time()

    (year, month, day, hour, minute, second, wday, yday) = latest_ds3231_time
    rp2040_rtc.datetime((year, month, day, wday, hour, minute, second, 0))
    print("set_pico_rtc_from_ds3231:", end='');
    print(latest_ds3231_time)
    print("ticks_for_transition:", end='');
    print(ticks_for_transition)
    print("hour:", end='');
    print(hour)
    print("minute:", end='');
    print(minute)
    print("second:", end='');
    print(second)
    picoTime = rp2040_rtc.datetime()
    print("secondsFromPico:", end='');
    print(picoTime[6])

    initial_pico_seconds = rp2040_rtc.datetime()[6]
    latest_pico_time = rp2040_rtc.datetime()
    ticks_for_pico_transition = ticks_ms()
    while latest_pico_time[6] is initial_pico_seconds:
        ticks_for_pico_transition = ticks_ms() % 1000
        latest_pico_time = rp2040_rtc.datetime()
    print("latest_pico_time:", end='');
    print(latest_pico_time)
    print("ticks_for_pico_transition:", end='');
    print(ticks_for_pico_transition)


set_pico_rtc_from_ds3231()


def secs_callback(t):
    picoTime = rp2040_rtc.datetime()
    picoSeconds = picoTime[6]
    picoMinutes = picoTime[5]
    epochSecond = picoSeconds + (picoMinutes * 60)
    print(f'wave pico rtc = {picoMinutes}m{picoSeconds}s')
    passphrase = treasurePassphrases.passphraseFor(epochSecond // 10)
    # print(f'passphrase = {passphrase}')
    display.clear()
    if (passphrase is not None):
        display.show_text(passphrase.words[epochSecond % 2])


scheduler.schedule("clock-second", 1000, secs_callback)

display.clear()
display.show_text("BONG")


def listenForUsbTimeSignal():
    lastSecondPrinted = None
    while True:
        picoTime = rp2040_rtc.datetime()
        ds3231Time = ds3231_rtc.get_time()
        secondsFromPico = picoTime[6]
        secondsFromDS3231Time = ds3231Time[5]
        if secondsFromPico != lastSecondPrinted:
            picoTime = rp2040_rtc.datetime()
            print('Pico   RTC :', end='');
            print(picoTime)
            print('DS3231 RTC :', end='');
            print(ds3231Time)
            print('Pico   seconds :', end='');
            print(secondsFromPico)
            print('DS3231 seconds :', end='');
            print(secondsFromDS3231Time)
            lastSecondPrinted = secondsFromPico
            led_onboard.toggle()

        receivedTimeDataFromUsb = readDeadlineAndTimeToDeadlineFromUSB()
        if receivedTimeDataFromUsb:
            deadLineFields, deadline_ticks = receivedTimeDataFromUsb
            print("deadLineFields: ", end='');
            print(deadLineFields)
            (year, month, day, hour, minute, second, wday, yday) = deadLineFields
            while ticks_diff(deadline_ticks, ticks_ms()) > 0:
                sleep_us(1000)  # *ticks_diff(deadline, time.ticks_ms())
            ds3231_rtc.save_time(deadLineFields)
            rp2040_rtc.datetime((year, month, day, wday, hour, minute, second, 0))
            print("Saved time from USB\t: ", end='');
            print(deadLineFields)
            print("PICO RTC says\t:", end='');
            print(rp2040_rtc.datetime())
            print("DS3231 now says\t:", end='');
            print(RTC().get_time())


listenForUsbTimeSignal()
