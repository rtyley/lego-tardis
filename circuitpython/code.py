import asyncio
from tardis import windows, tardis_keypad

print("HIHI")
windows.sweep()


async def main():
    await asyncio.gather(
        asyncio.create_task(windows.whoosh()),
        asyncio.create_task(tardis_keypad.catch_pin_transitions())
    )
    print("done")


asyncio.run(main())

# tardis.onKeys(Pressed(All), setMode(TakeOffAndSleep))
# tardis.onKeys(Released(All), setMode(Scrabble))
# tardis.onKeys(KeySequence(1,4,12), setMode(SetTime))

# tardis.start()
