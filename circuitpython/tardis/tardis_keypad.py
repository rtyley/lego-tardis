import asyncio
import board
import keypad
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
from adafruit_itertools.adafruit_itertools import takewhile

from tardis import ghetto_blaster

KEY_PINS = (
    board.SW0, board.SW1, board.SW2, board.SW3,
    board.SW4, board.SW5, board.SW6, board.SW7,
    board.SW8, board.SW9, board.SW10, board.SW11,
    board.SW12, board.SW13, board.SW14, board.SW15
)

i2c = board.I2C()
pixels = KeyPadLeds(i2c)

key_hist = [frozenset()]


async def catch_pin_transitions(ghetto_blaster_controls):
    with keypad.Keys(KEY_PINS, value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                idx = event.key_number

                previous_state = key_hist[-1]

                event_key = frozenset([idx])
                new_state = previous_state - event_key if event.released else previous_state | event_key

                key_hist.append(new_state)
                if len(key_hist) > 32:
                    del key_hist[0]

                print(new_state)
                print(len(key_hist))
                print([set(x) for x in key_hist[-5:]])

                def foo(x):
                    return len(x) <= 1

                single_key_stuff = \
                    list(reversed(list(map(lambda x: next(iter(x)), filter(lambda c: len(c) == 1, takewhile(foo, reversed(key_hist)))))))

                print(single_key_stuff[-2:])

                pixel_x = idx % 4
                pixel_y = idx // 4
                if event.pressed:
                    if single_key_stuff[-2:] == [0, 1]:
                        print("I LIKES YA")
                        ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayIAmTheDoctor)

                    if single_key_stuff[-2:] == [2, 3]:
                        ghetto_blaster_controls.make_request_for(ghetto_blaster.PauseOrResume())

                    print("pin went low")
                    pixels.pixelrgb(pixel_x, pixel_y, 255, 128, 64)
                elif event.released:
                    print("pin went high")
                    pixels.pixelrgb(pixel_x, pixel_y, 4, 8, 16)
            await asyncio.sleep(0)

