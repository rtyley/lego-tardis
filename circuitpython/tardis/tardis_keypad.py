import asyncio
import board
import keypad
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
from adafruit_itertools import takewhile

from tardis import ghetto_blaster, windows

# KEY_PIN_ARRAY = [
#     [board.SW0, board.SW1, board.SW2, board.SW3],
#     [board.SW4, board.SW5, board.SW6, board.SW7],
#     [board.SW8, board.SW9, board.SW10, board.SW11],
#     [board.SW12, board.SW13, board.SW14, board.SW15]
# ]

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

        print([set(x) for x in self.key_hist[-5:]])

    def single_key_hist(self):
        def foo(x):
            return len(x) <= 1
        single_key_stuff = \
            list(reversed(
                list(map(lambda x: next(iter(x)), filter(lambda c: len(c) == 1, takewhile(foo, reversed(self.key_hist)))))))

        print(single_key_stuff[-2:])
        return single_key_stuff


async def catch_pin_transitions(key_history: KeyHistory, ghetto_blaster_controls):
    anim = None
    with keypad.Keys(KEY_PINS, value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                idx = event.key_number
                key_history.add_event(event)

                single_key_stuff = key_history.single_key_hist()

                if event.pressed:
                    if single_key_stuff[-2:] == [0, 1]:
                        ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayIAmTheDoctor)
                    if single_key_stuff[-2:] == [1, 0]:
                        ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayTardisLanding)
                    if single_key_stuff[-2:] == [14, 15]:
                        anim = asyncio.create_task(windows.whooshy_cycle())

                    if single_key_stuff[-2:] == [2, 3]:
                        ghetto_blaster_controls.make_request_for(ghetto_blaster.PauseOrResume())

                    print("pin went low")
                    colour = (255, 128, 64)
                elif event.released:
                    print("pin went high")
                    colour = (4, 8, 16)

                pixel_x = idx % 4
                pixel_y = idx // 4
                pixels.pixelrgb(pixel_x, pixel_y, colour[0], colour[1], colour[2])
            await asyncio.sleep(0)

