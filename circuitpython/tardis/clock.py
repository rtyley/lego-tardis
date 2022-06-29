import board
import adafruit_ds3231  # battery-backed RTC

i2c = board.I2C()
batteryRTC = adafruit_ds3231.DS3231(i2c)

t = batteryRTC.datetime
print(t)  # uncomment for debugging
