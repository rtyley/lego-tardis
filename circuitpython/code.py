import math
import time

from tardis import windows

print("HIHI")
windows.sweep()


windows.aw.set_constant_current(1, 255)
for lamp_angle in range(1000):
    windows.set_windows([int(255 * math.pow((1 + math.cos((2 * math.pi * x/8) - (lamp_angle / 10)))/2, 2)) for x in range(8)])
    time.sleep(0.01)

from tardis import tardis_keypad

# tardis.onKeys(Pressed(All), setMode(TakeOffAndSleep))
# tardis.onKeys(Released(All), setMode(Scrabble))
# tardis.onKeys(KeySequence(1,4,12), setMode(SetTime))

# tardis.set_all_windows(255)

# tardis.start()
