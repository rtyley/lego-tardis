import audiobusio
from digitalio import DigitalInOut, Direction
from time import sleep


class I2SPins:
    """
    Abstract class providing common interface for the audio pins
    Subclasses should fill _xxx and _yyy properties.
    """

    def create_i2s_out(self):
        return audiobusio.I2SOut(
            self.bit_clock,
            self.word_select,
            self.data
        )

    def diagnostic_check(self):
        pins = {
            'bit_clock - BLACK(GPIO 0)': self.bit_clock,
            'word_select - BROWN(GPIO 1)': self.word_select,
            'data - BLUE(GPIO 3)': self.data
        }

        for pin_name, boardPin in pins.items():
            pin = DigitalInOut(boardPin)
            pin.direction = Direction.OUTPUT
            print(pin_name)
            for x in range(3):
                pin.value = True
                print("HIGH")
                sleep(2)
                pin.value = False
                print("LOW")
                sleep(2)
