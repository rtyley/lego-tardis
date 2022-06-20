import math
import supervisor as supervisor
from pmk.platform.keybow2040 import Keybow2040  # keypad
from pmk import PMK
import adafruit_aw9523  # LED driver
import adafruit_ds3231  # battery-backed RTC
import board
import audiobusio
import audiomp3

keybow2040 = Keybow2040()
pmk = PMK(keybow2040)
i2c = keybow2040.i2c()
aw = adafruit_aw9523.AW9523(i2c)
audio = audiobusio.I2SOut(board.GP0, board.GP1, board.INT)

batteryRTC = adafruit_ds3231.DS3231(i2c)
t = batteryRTC.datetime
print(t)  # uncomment for debugging

windowPinNumbers = [1, 4, 2, 5, 3, 6, 7, 12]
# 1: 1_Black
# 2: 2_Black
# 3: 3_Black
# 4: 1_White
# 5: 2_White
# 6: 3_White
# 7: 4_Black
# 12: 4_White


# Set all pins to outputs and LED (const current) mode
aw.LED_modes = 0xFFFF
aw.directions = 0xFFFF


def start():
    while True:
        pmk.update()
        now_ticks = supervisor.ticks_ms()
        print(now_ticks, batteryRTC.datetime)
        cycle_duration = 2000
        cycle_proportion = (now_ticks % cycle_duration) / cycle_duration
        num_keys_pressed = len(pmk.get_pressed())
        level = int((0.5 + (0.5*(num_keys_pressed / 16))) * (128 + 127 * (math.sin(cycle_proportion * 2 * math.pi))))
        set_all_windows(level)
        time.sleep(0.01)


__led_buffer = bytearray(9)


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



# from audiocore import WaveFile
#wave_file = open("TARDIS_Remastered_Short_01.wav", "rb")
#wave = WaveFile(wave_file)
#audio.play(wave)
#print("playing", wave_file)

mp3 = audiomp3.MP3Decoder(open("IAmTheDoctor.Part1.40kbps.mp3", "rb"))
audio.play(mp3)

# This allows you to do other things while the audio plays!
while audio.playing:
    pass
