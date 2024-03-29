import asyncio
import board
import keypad
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
from adafruit_itertools import takewhile
import supervisor
from adafruit_ticks import ticks_diff
import math

from tardis.device_mode import DeviceMode

KEY_PINS = (
    board.SW0, board.SW1, board.SW2, board.SW3,
    board.SW4, board.SW5, board.SW6, board.SW7,
    board.SW8, board.SW9, board.SW10, board.SW11,
    board.SW12, board.SW13, board.SW14, board.SW15
)

i2c = board.I2C()
pixels = KeyPadLeds(i2c)


class KeyHistory:
    def __init__(self):
        self.key_hist = [frozenset()]

    def add_event(self, event: keypad.Event):
        previous_state = self.key_hist[-1]

        event_key = frozenset([event.key_number])
        new_state = previous_state - event_key if event.released else previous_state | event_key

        self.key_hist.append(new_state)
        if len(self.key_hist) > 32:
            del self.key_hist[0]

        # print([set(x) for x in self.key_hist[-5:]])

    def single_key_hist(self):
        def foo(x):
            return len(x) <= 1
        single_key_stuff = \
            list(reversed(
                list(map(lambda x: next(iter(x)), filter(lambda c: len(c) == 1, takewhile(foo, reversed(self.key_hist)))))))

        print(single_key_stuff[-2:])
        return single_key_stuff


async def show_lights():
    while True:
        for idx in range(16):
            pixel_x = idx % 4
            pixel_y = idx // 4

            pixels.pixelrgb(pixel_x, pixel_y, 255, 255, 255)
            await asyncio.sleep(1)
            # pixels.pixelrgb(pixel_x, pixel_y, 0, 0, 0)
            await asyncio.sleep(1)

def set_key(key_num, r, g, b):
    pixel_x = key_num % 4
    pixel_y = key_num // 4

    pixels.pixelrgb(pixel_x, pixel_y, r, g, b)


def set_control_light(raw_level):
    pixels.pixelrgb(0, 1, raw_level, raw_level, raw_level)

async def test_control_light():
    while True:
        set_control_light(0)
        await asyncio.sleep(0.5)
        set_control_light(33) # With LiPo source, 33 is full off, 34 is faint
        await asyncio.sleep(0.5)

async def throb_control_light():
    start_time = supervisor.ticks_ms()
    base = 0
    set_control_light(0)
    await asyncio.sleep(4)
    sweep = 255 - base
    while True:
        now = supervisor.ticks_ms()
        time_since_start = ticks_diff(now, start_time)
        level = base + int((sweep * ((1 + math.cos(time_since_start/500))/2)))
        set_control_light(level)
        await asyncio.sleep(0.02)


async def catch_pin_transitions(key_history: KeyHistory, device_mode: DeviceMode):
    with keypad.Keys(KEY_PINS, value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                key_history.add_event(event)
                single_key_stuff = key_history.single_key_hist()

                idx = event.key_number
                pixel_x = idx % 4
                pixel_y = idx // 4
                k = (pixel_x, pixel_y)
                print(f'k: {k} idx: {idx}')
                # if event.pressed:
                #     print("pin went low")
                # elif event.released:
                #     print("pin went high")
                device_mode.get_activity().handle_key(event, k, single_key_stuff)
            await asyncio.sleep(0)

