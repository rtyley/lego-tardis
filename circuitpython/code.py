import math
import time
import asyncio

from tardis import windows, tardis_keypad

print("HIHI")
windows.sweep()


async def main():
    # led2_task = asyncio.create_task(blink(board.D2, 0.1, 20))

    await asyncio.gather(
        asyncio.create_task(windows.whoosh()),
        asyncio.create_task(tardis_keypad.catch_pin_transitions())
    )  # Don't forget "await"!
    print("done")


asyncio.run(main())



from tardis import tardis_keypad

# tardis.onKeys(Pressed(All), setMode(TakeOffAndSleep))
# tardis.onKeys(Released(All), setMode(Scrabble))
# tardis.onKeys(KeySequence(1,4,12), setMode(SetTime))

# tardis.set_all_windows(255)

# tardis.start()
