from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
import board
import keypad
import tardis.windows
from tardis.device_mode import Activity
from tardis import ghetto_blaster, windows, clock, tardis_keypad
import asyncio

from tardis.treasure.passphrases import TreasurePassphrases

i2c = board.I2C()
pixels = KeyPadLeds(i2c)

class EpochState:

    def __init__(self, passphrase, passphrase_epoch: int):
        self.passphrase_epoch = passphrase_epoch
        self.passphrase = passphrase
        print(f'password is {passphrase.fullText}')
        self.correct_keys = [TreasureHunt.keyNumByWord[word] for word in passphrase.words]
        self.unsolved = True

    def is_solved_by(self, latest_keys) -> bool:
        if self.unsolved and latest_keys[-2:] == self.correct_keys:
            self.unsolved = False
            return True
        else:
            return False


class TreasureHunt(Activity):
    treasurePassphrases = TreasurePassphrases([
        "Freedom-Pattern-Drum-Origin-2",
        "Zoo-Child-Century-Weave-Faint-1"
    ])

    keyNumByWord = {
        "GOOD": 12,
        "BAD": 8,
        "DRY": 13,
        "WET": 9,
        "FUN": 14,
        "SLY": 10,
        "HOT": 15,
        "TOP": 11,
        "ANT": 4,
        "BEE": 0,
        "CAT": 5,
        "DOG": 1,
        "FOX": 6,
        "PIG": 2,
        "YAK": 7,
        "WOLF": 3
    }

    wordByKeyNum = {v: k for k, v in keyNumByWord.items()}

    def __init__(self, ghetto_blaster_controls: ghetto_blaster.Controls):
        # self.dev_mode = dev_mode
        self.ghetto_blaster_controls = ghetto_blaster_controls
        self.score = 0
        self.epoch_state = None

    def ensure_epoch_state_up_to_date(self) -> EpochState:
        t = clock.rp2040_rtc.datetime
        print(f'keybow pico rtc: {t.tm_min}m{t.tm_sec}s')
        passphrase_epoch = ((t.tm_min * 60) + t.tm_sec) // 10
        if self.epoch_state is None or self.epoch_state.passphrase_epoch != passphrase_epoch:
            tardis_keypad.set_key(0, 255 if passphrase_epoch % 2 == 0 else 0, 0, 0)
            self.epoch_state = EpochState(TreasureHunt.treasurePassphrases.passphraseFor(passphrase_epoch), passphrase_epoch)
        return self.epoch_state

    async def start(self):
        tardis.windows.set_all_windows(0)
        while True:
            # print("The time is {}:{:02}:{:02}".format(t.tm_hour, t.tm_min, t.tm_sec))
            # passphrase = treasurePassphrases.passphraseFor((t.tm_min * 60) + t.tm_sec)
            self.ensure_epoch_state_up_to_date()

            windows.set_windows(
                [255 if (x // 4 <= self.score) else 0 for x in range(8)]
            )
            await asyncio.sleep(1)

    def handle_key(self, event: keypad.Event, coords, single_key_stuff):
        if event.pressed:
            colour = (255, 255, 0)
            #  print(f'event.key_number: {event.key_number} , word: {TreasureHunt.wordByKeyNum[event.key_number]}')
        elif event.released:
            colour = (255, 255, 255)
        pixels.pixelrgb(coords[0], coords[1], colour[0], colour[1], colour[2])


        epoch_state = self.ensure_epoch_state_up_to_date()
        if epoch_state.is_solved_by(single_key_stuff):
            self.score += 1
            print(f'score: {self.score}')
            if self.score == 1:
                print("It begins!")
                # self.ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayIAmTheDoctor)
            elif self.score == 4:
                self.ghetto_blaster_controls.make_request_for(ghetto_blaster.PlayTardisLanding)
                asyncio.create_task(windows.whooshy_cycle())

