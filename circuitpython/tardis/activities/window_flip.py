import random
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
import board
import keypad
import tardis.windows
from tardis.device_mode import Activity

i2c = board.I2C()
pixels = KeyPadLeds(i2c)


class WindowFlip(Activity):
    window_buf = [False] * tardis.windows.NUM_WINDOWS

    async def start(self):
        pass

    def handle_key(self, event: keypad.Event, coords, single_key_stuff):
        if event.pressed:
            self.flip_random_window()
            colour = (255, 255, 0)
        elif event.released:
            colour = (255, 255, 255)

        pixels.pixelrgb(coords[0], coords[1], colour[0], colour[1], colour[2])

    def flip_random_window(self):
        window_index = random.randint(0, tardis.windows.NUM_WINDOWS)
        lit = not self.window_buf[window_index]
        tardis.windows.set_window_on(window_index, lit)
        self.window_buf[window_index] = lit
