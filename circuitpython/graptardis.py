import math
import time
import supervisor as supervisor
import adafruit_ds3231  # battery-backed RTC
import board
import audiobusio
import audiomp3

import asyncio
import board
from simpleio import map_range


i2c = board.I2C()





audio = audiobusio.I2SOut(board.GP0, board.GP1, board.INT)





def start():
    while True:
        now_ticks = supervisor.ticks_ms()
        print(now_ticks, batteryRTC.datetime)
        cycle_duration = 2000
        cycle_proportion = (now_ticks % cycle_duration) / cycle_duration
        level = map_range(math.sin(cycle_proportion * 2 * math.pi), -1 , 1, 0, 224)
        set_all_windows(level)
        time.sleep(0.01)

mp3 = audiomp3.MP3Decoder(open("IAmTheDoctor.Part1.40kbps.mp3", "rb"))
audio.play(mp3)

# This allows you to do other things while the audio plays!
while audio.playing:
    pass
