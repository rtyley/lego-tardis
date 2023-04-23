import asyncio

from tardis import tardis_keypad, windows, ghetto_blaster, home_menu, device_mode  # , memory_game

# from tardis import sound
import board

from tardis.device_mode import DeviceMode
from tardis.hardware.keybow2040 import KeyBow2040I2SPins as I2SPins
import tardis.clock
from tardis.memory_game import MemoryGame

print("HIHI")


# I2SPins().diagnostic_check()


async def main():
    await asyncio.sleep(0.5)
    ghetto_blaster_controls = ghetto_blaster.Controls()
    key_history = tardis_keypad.KeyHistory()
    dev_mode = DeviceMode(home_menu.HomeMenu(ghetto_blaster_controls))
    dev_mode.set_activity(MemoryGame())

    await asyncio.gather(
        asyncio.create_task(windows.whoosh()),
        # asyncio.create_task(tardis.clock.watch_clock()),

        asyncio.create_task(tardis_keypad.catch_pin_transitions(key_history, dev_mode)),

        # asyncio.create_task(tardis_keypad.throb_control_light()),

        asyncio.create_task(ghetto_blaster.poll_for_music_requests(ghetto_blaster_controls))
    )
    print("doneish")


asyncio.run(main())

# tardis.onKeys(Pressed(All), setMode(TakeOffAndSleep))
# tardis.onKeys(Released(All), setMode(Scrabble))
# tardis.onKeys(KeySequence(KEY[0][0],KEY[1][0],KEY[0][-1]), setMode(SetTime))

# tardis.start()
