import random
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
import board
import keypad
import tardis.windows
from tardis.device_mode import Activity
from random import randrange

i2c = board.I2C()
pixels = KeyPadLeds(i2c)


class WindowFlip(Activity):
    window_buf = [False] * tardis.windows.NUM_WINDOWS

    async def start(self):
        pass

    def handle_key(self, event: keypad.Event, coords, single_key_stuff):
        self.flip_random_window()
        if event.pressed:
            colour = (255, 255, 0)
        elif event.released:
            colour = (255, 255, 255)
        pixels.pixelrgb(coords[0], coords[1], colour[0], colour[1], colour[2])
        if (randrange(3)==0):
            pixels.pixelrgb(randrange(4), randrange(4), randrange(255), randrange(255), randrange(255))

    def flip_random_window(self):
        window_index = random.randrange(int(tardis.windows.NUM_WINDOWS / 2))
        print(window_index)
        lit = not self.window_buf[window_index]
        tardis.windows.set_window_on(window_index, lit)
        tardis.windows.set_window_on(window_index + int(tardis.windows.NUM_WINDOWS / 2), lit)
        self.window_buf[window_index] = lit
