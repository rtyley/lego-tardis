import asyncio
import board
import keypad
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
from adafruit_itertools.adafruit_itertools import takewhile

from tardis import sound

KEY_PINS = (
    board.SW0, board.SW1, board.SW2, board.SW3,
    board.SW4, board.SW5, board.SW6, board.SW7,
    board.SW8, board.SW9, board.SW10, board.SW11,
    board.SW12, board.SW13, board.SW14, board.SW15
)

i2c = board.I2C()
pixels = KeyPadLeds(i2c)

key_hist = [frozenset()]


async def catch_pin_transitions():
    """Print a message when pin goes  low and when it goes high."""
    with keypad.Keys(KEY_PINS, value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                print(event.key_number)
                idx = event.key_number

                previous_state = key_hist[-1]
                if event.released:
                    print("REMOVING")
                    new_state = previous_state - frozenset([idx])
                else:
                    print("ADDING")
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
                if single_key_stuff[-2:] == [0, 1]:
                    print("I LIKES YA")
                    sound.play_music()

                if event.pressed:
                    print("pin went low")
                    pixels.pixelrgb(idx % 4, idx // 4, 255, 128, 64)
                elif event.released:
                    print("pin went high")
                    pixels.pixelrgb(idx % 4, idx // 4, 4, 8, 16)
            await asyncio.sleep(0)

