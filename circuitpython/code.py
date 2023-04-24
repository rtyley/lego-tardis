import asyncio

from tardis import tardis_keypad, windows, ghetto_blaster  # , memory_game
from tardis.activities import home_menu

from tardis.device_mode import DeviceMode
from tardis.activities.memory_game import MemoryGame

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
