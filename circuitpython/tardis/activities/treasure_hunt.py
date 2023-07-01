import random
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
import board
import keypad
import tardis.windows
from tardis.device_mode import Activity
from tardis import ghetto_blaster, windows
import asyncio

i2c = board.I2C()
pixels = KeyPadLeds(i2c)


class TreasureHunt(Activity):
    window_buf = [False] * tardis.windows.NUM_WINDOWS

    lastCorrectPassPhrase = None
    score = 0

    def __init__(self, ghetto_blaster_controls: ghetto_blaster.Controls):
        # self.dev_mode = dev_mode
        self.ghetto_blaster_controls = ghetto_blaster_controls

    async def start(self):
        tardis.windows.set_all_windows(0)
        pass

    def handle_key(self, event: keypad.Event, coords, single_key_stuff):
        if event.pressed:
            colour = (255, 255, 0)
        elif event.released:
            colour = (255, 255, 255)
        pixels.pixelrgb(coords[0], coords[1], colour[0], colour[1], colour[2])

        if True:
            self.score += 1
            if self.score == 1:
                self.ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayIAmTheDoctor)
            elif self.score == 4:
                self.ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayTardisLanding)
                asyncio.create_task(windows.whooshy_cycle())

