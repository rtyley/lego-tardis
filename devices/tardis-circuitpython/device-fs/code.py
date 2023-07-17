import asyncio

from tardis import tardis_keypad, ghetto_blaster, clock  # , memory_game
from tardis.activities.window_flip import WindowFlip
from tardis.device_mode import DeviceMode
from clocks.cp_real_time_clocks import all_clocks
from clocks.synchro import ClockReporter

# I2SPins().diagnostic_check()


async def main():
    clock.set_rp2040_rtc_from_battery_rtc()
    await asyncio.sleep(0.5)
    ghetto_blaster_controls = ghetto_blaster.Controls()
    key_history = tardis_keypad.KeyHistory()
    dev_mode = DeviceMode()
    # dev_mode.set_activity(TreasureHunt(ghetto_blaster_controls))
    dev_mode.set_activity(WindowFlip(ghetto_blaster_controls))

    for c in all_clocks:
        asyncio.create_task(ClockReporter(c).start())

    # rp2040_rtc_reporter.start()
    await asyncio.gather(
        # asyncio.create_task(windows.whoosh()),
        asyncio.create_task(clock.watch_clock()),

        asyncio.create_task(tardis_keypad.catch_pin_transitions(key_history, dev_mode)),

        # asyncio.create_task(tardis_keypad.throb_control_light()),

        asyncio.create_task(ghetto_blaster.poll_for_music_requests(ghetto_blaster_controls))
    )
    print("doneish")


asyncio.run(main())
