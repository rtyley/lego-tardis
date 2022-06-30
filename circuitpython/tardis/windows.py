import time

import adafruit_aw9523  # LED driver
import board

i2c = board.I2C()
aw = adafruit_aw9523.AW9523(i2c)

# Set all pins to outputs and LED (const current) mode
aw.LED_modes = 0xFFFF
aw.directions = 0xFFFF
aw.constant_current_range = adafruit_aw9523.AW9523_2_4_RANGE

__led_buffer = bytearray(9)

windowPinNumbers = [1, 4, 2, 5, 3, 6, 7, 12]
# 1: 1_Black
# 2: 2_Black
# 3: 3_Black
# 4: 1_White
# 5: 2_White
# 6: 3_White
# 7: 4_Black
# 12: 4_White

NUM_WINDOWS = 8

def sweep():
    half_num_windows = int(NUM_WINDOWS / 2)
    for n in range(3):
        for windowIndex in range(half_num_windows):
            aw.set_constant_current(windowPinNumbers[windowIndex], 224)
            aw.set_constant_current(windowPinNumbers[windowIndex+half_num_windows], 224)
            time.sleep(0.1)
            aw.set_constant_current(windowPinNumbers[windowIndex], 0)
            aw.set_constant_current(windowPinNumbers[windowIndex + half_num_windows], 0)


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


def set_windows(values):
    __led_buffer[0] = 0x25  # Address of the register for the 1st pin (P0_1 LED current control)

    __led_buffer[1] = values[0]
    __led_buffer[2] = values[2]  # int(value/3)
    __led_buffer[3] = values[4]  # int(values[]/5)
    __led_buffer[4] = values[1]  # int(values[]/2)
    __led_buffer[5] = values[3]  # int(values[]/4)
    __led_buffer[6] = values[5]  # int(values[]/6)
    __led_buffer[7] = values[6]  # int(values[]/7)
    __led_buffer[8] = values[7]  # int(values[]/8)
    with aw.i2c_device as i2cDev:
        i2cDev.write(__led_buffer)