# import tardis

import asyncio
import board
import keypad
from adafruit_is31fl3731.keybow2040 import Keybow2040 as Pixels

KEY_PINS = (
    board.SW0,
    board.SW1,
    board.SW2,
    board.SW3,
    board.SW4,
    board.SW5,
    board.SW6,
    board.SW7,
    board.SW8,
    board.SW9,
    board.SW10,
    board.SW11,
    board.SW12,
    board.SW13,
    board.SW14,
    board.SW15
)

pixels = Pixels(board.I2C())

idx =0



async def catch_pin_transitions(pin):
    print(f"We have to try {pin}")
    """Print a message when pin goes  low and when it goes high."""
    with keypad.Keys(KEY_PINS, value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                print(event.key_number)
                idx = event.key_number
                if event.pressed:
                    print("pin went low")
                    pixels.pixelrgb(idx % 4, idx // 4, 255, 128, 64)
                elif event.released:
                    print("pin went high")
                    pixels.pixelrgb(idx % 4, idx // 4, 4, 8, 16)
            await asyncio.sleep(0)


async def main():
    interrupt_task = asyncio.create_task(catch_pin_transitions(board.SW0))
    await asyncio.gather(interrupt_task)

asyncio.run(main())

# tardis.onKeys(Pressed(All), setMode(TakeOffAndSleep))
# tardis.onKeys(Released(All), setMode(Scrabble))
# tardis.onKeys(KeySequence(1,4,12), setMode(SetTime))

# tardis.set_all_windows(255)

# tardis.start()
