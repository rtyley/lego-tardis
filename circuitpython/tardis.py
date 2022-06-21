import math
import time
import supervisor as supervisor
import adafruit_aw9523  # LED driver
import adafruit_ds3231  # battery-backed RTC
import board
import audiobusio
import audiomp3

import asyncio
import board
import keypad
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
from adafruit_itertools.adafruit_itertools import takewhile

KEY_PINS = (
    board.SW0, board.SW1, board.SW2, board.SW3,
    board.SW4, board.SW5, board.SW6, board.SW7,
    board.SW8, board.SW9, board.SW10, board.SW11,
    board.SW12, board.SW13, board.SW14, board.SW15
)

i2c = board.I2C()
pixels = KeyPadLeds(i2c)

key_hist = [frozenset()]


async def catch_pin_transitions(pin):
    print(f"We have to try {pin}")
    """Print a message when pin goes  low and when it goes high."""
    with keypad.Keys(KEY_PINS, value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                print(event.key_number)
                idx = event.key_number

                previous_state = key_hist[-1]
                if event.released:
                    new_state = previous_state - frozenset([idx])
                else:
                    new_state = previous_state | frozenset([idx])
                key_hist.append(new_state)
                if len(key_hist) > 32:
                    del key_hist[0]

                print(new_state)
                print(len(key_hist))
                print(key_hist[-4:])

                def foo(x):
                    return len(x) <= 1

                single_key_stuff = \
                    list(reversed(list(map(lambda x: next(iter(x)), filter(lambda c: len(c) == 1, takewhile(foo, reversed(key_hist)))))))

                print(single_key_stuff[-2:])
                if single_key_stuff[-2:] == [0,1]:
                    print("I LIKES YA")

                if event.pressed:
                    print("pin went low")
                    pixels.pixelrgb(idx % 4, idx // 4, 255, 128, 64)
                elif event.released:
                    print("pin went high")
                    pixels.pixelrgb(idx % 4, idx // 4, 4, 8, 16)
            await asyncio.sleep(0)


async def main():
    interrupt_task = asyncio.create_task(catch_pin_transitions(board.SW0))
    await asyncio.gather(interrupt_task)


asyncio.run(main())

aw = adafruit_aw9523.AW9523(i2c)
audio = audiobusio.I2SOut(board.GP0, board.GP1, board.INT)

batteryRTC = adafruit_ds3231.DS3231(i2c)
t = batteryRTC.datetime
print(t)  # uncomment for debugging

windowPinNumbers = [1, 4, 2, 5, 3, 6, 7, 12]
# 1: 1_Black
# 2: 2_Black
# 3: 3_Black
# 4: 1_White
# 5: 2_White
# 6: 3_White
# 7: 4_Black
# 12: 4_White


# Set all pins to outputs and LED (const current) mode
aw.LED_modes = 0xFFFF
aw.directions = 0xFFFF


def start():
    while True:
        now_ticks = supervisor.ticks_ms()
        print(now_ticks, batteryRTC.datetime)
        cycle_duration = 2000
        cycle_proportion = (now_ticks % cycle_duration) / cycle_duration
        level = int(128 + 127 * (math.sin(cycle_proportion * 2 * math.pi)))
        set_all_windows(level)
        time.sleep(0.01)


__led_buffer = bytearray(9)


def set_all_windows(value):
    __led_buffer[0] = 0x25  # Address of the register for the 1st pin (P0_1 LED current control)
    __led_buffer[1] = value  # int(value/1)
    __led_buffer[2] = value  # int(value/3)
    __led_buffer[3] = value  # int(value/5)
    __led_buffer[4] = value  # int(value/2)
    __led_buffer[5] = value  # int(value/4)
    __led_buffer[6] = value  # int(value/6)
    __led_buffer[7] = value  # int(value/7)
    __led_buffer[8] = value  # int(value/8)
    with aw.i2c_device as i2cDev:
        i2cDev.write(__led_buffer)


mp3 = audiomp3.MP3Decoder(open("IAmTheDoctor.Part1.40kbps.mp3", "rb"))
audio.play(mp3)

# This allows you to do other things while the audio plays!
while audio.playing:
    pass
