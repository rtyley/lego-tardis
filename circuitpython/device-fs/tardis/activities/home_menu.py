import asyncio
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
import board

from tardis import ghetto_blaster, windows
from tardis.device_mode import Activity

i2c = board.I2C()
pixels = KeyPadLeds(i2c)


class HomeMenu(Activity):
    def __init__(self, ghetto_blaster_controls: ghetto_blaster.Controls):
        # self.dev_mode = dev_mode
        self.ghetto_blaster_controls = ghetto_blaster_controls

    async def start(self):
        pass

    def handle_key(self, event, coords, single_key_stuff):
        if event.pressed:
            last_2_keys = single_key_stuff[-2:]

            # if last_2_keys == [12, 13]:
            #     self.dev_mode.set_activity(MemoryGame())

            if last_2_keys == [0, 1]:
                self.ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayIAmTheDoctor)
            if last_2_keys == [9, 10]:
                self.ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayOriginalTheme)
            if last_2_keys == [1, 0]:
                self.ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayTardisLanding)
            if last_2_keys == [14, 15]:
                asyncio.create_task(windows.whooshy_cycle())
            if last_2_keys == [2, 3]:
                self.ghetto_blaster_controls.make_request_for(ghetto_blaster.PauseOrResume())

            colour = (255, 255, 0)
        elif event.released:
            colour = (255, 255, 255)

        pixels.pixelrgb(coords[0], coords[1], colour[0], colour[1], colour[2])
