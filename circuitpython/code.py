import asyncio


from tardis.device_mode import DeviceMode
from tardis import tardis_keypad, windows, ghetto_blaster  # , memory_game
from tardis.activities.home_menu import HomeMenu
from tardis.activities.memory_game import MemoryGame
from tardis.activities.window_flip import WindowFlip

print("HIHI")


# I2SPins().diagnostic_check()


async def main():
    await asyncio.sleep(0.5)
    ghetto_blaster_controls = ghetto_blaster.Controls()
    key_history = tardis_keypad.KeyHistory()
    dev_mode = DeviceMode()
    dev_mode.set_activity(HomeMenu(ghetto_blaster_controls))

    await asyncio.gather(
        asyncio.create_task(windows.whoosh()),
        # asyncio.create_task(tardis.clock.watch_clock()),

        asyncio.create_task(tardis_keypad.catch_pin_transitions(key_history, dev_mode)),

        # asyncio.create_task(tardis_keypad.throb_control_light()),

        asyncio.create_task(ghetto_blaster.poll_for_music_requests(ghetto_blaster_controls))
    )
    print("doneish")


asyncio.run(main())

# tardis.start()
