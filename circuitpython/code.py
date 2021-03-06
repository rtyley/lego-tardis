import asyncio

from tardis import tardis_keypad, windows, ghetto_blaster

# from tardis import sound
import board
from tardis.hardware.keybow2040 import KeyBow2040I2SPins as I2SPins

print("HIHI")

# I2SPins().diagnostic_check()


# windows.sweep()


async def main():
    ghetto_blaster_controls = ghetto_blaster.Controls()
    key_history = tardis_keypad.KeyHistory()

    await asyncio.gather(
        asyncio.create_task(windows.whoosh(key_history)),
        asyncio.create_task(tardis_keypad.catch_pin_transitions(key_history, ghetto_blaster_controls)),
        asyncio.create_task(ghetto_blaster.poll_for_music_requests(ghetto_blaster_controls))
    )
    print("done")


asyncio.run(main())

# tardis.onKeys(Pressed(All), setMode(TakeOffAndSleep))
# tardis.onKeys(Released(All), setMode(Scrabble))
# tardis.onKeys(KeySequence(KEY[0][0],KEY[1][0],KEY[0][-1]), setMode(SetTime))

# tardis.start()
