import board
import adafruit_ds3231  # battery-backed RTC
import supervisor
import time

i2c = board.I2C()
batteryRTC = adafruit_ds3231.DS3231(i2c)

t = batteryRTC.datetime
print(t)  # uncomment for debugging

async def whoosh():
    start_time = supervisor.ticks_ms()
    while True:
        now = supervisor.ticks_ms()
        time_since_start = ticks_diff(now, start_time)
        # print(f"time_since_start= {time_since_start}")
        lamp_angle = time_since_start / 500
        set_windows(
            [int(255 * math.pow((1 + math.cos(1 * ((2 * math.pi * x / 8) - lamp_angle))) / 2, 8)) for x in
             range(8)]
        )
        await asyncio.sleep(0.02)