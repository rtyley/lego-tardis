import random
import time

import audiobusio
import asyncio
from adafruit_is31fl3731.keybow2040 import Keybow2040 as KeyPadLeds
import array
import math
import board
from audiocore import RawSample
import keypad

from tardis.device_mode import Activity

i2c = board.I2C()
pixels = KeyPadLeds(i2c)


def note_freq(name):
    octave = int(name[-1])
    PITCHES = "c,c#,d,d#,e,f,f#,g,g#,a,a#,b".split(",")
    pitch = PITCHES.index(name[:-1].lower())
    print(name)
    print(pitch)
    print(octave)
    return 440 * 2 ** ((octave - 4) + (pitch - 9) / 12.)


class Element:

    def __init__(self, note, colour, quadrant_vector):
        self.note = note
        self.colour = colour
        self.note_f = note_freq(self.note)
        self.quadrant_vector = quadrant_vector

        (qx, qy) = quadrant_vector

        def keyFor(x, y):
            return int(1.5 + (x * qx) + (qx / 2)), int(1.5 + (y * qy) + (qy / 2))

        self.resting_key = keyFor(0, 0)
        self.other_keys = [keyFor(0, 1), keyFor(1, 1), keyFor(1, 0)]
        self.all_keys = [self.resting_key] + self.other_keys

    def set_button(self, activate):
        def set_key(key, mult):
            c = self.colour
            pixels.pixelrgb(key[0], key[1], int(c[0] * mult), int(c[1] * mult), int(c[2] * mult))

        set_key(self.resting_key, 1 if activate else 0.2)
        for k in self.other_keys:
            set_key(k, 1 if activate else 0)

    def start_element(self):
        self.set_button(True)
        tone_volume = 0.01  # Increase this to increase the volume of the tone.
        frequency = self.note_f  # Set this to the Hz of the tone you want to generate.
        length = math.floor(8000 / frequency)
        print(length)
        sine_wave = array.array("H", [0] * length)
        for i in range(length):
            sine_wave[i] = int((1 + math.sin(math.pi * 2 * i / length)) * tone_volume * (2 ** 15 - 1))
        sine_wave_sample = RawSample(sine_wave)
        # print("sine_wave_sample.sample_rate")
        # print(sine_wave_sample.sample_rate)
        mixer.voice[0].play(sine_wave_sample, loop=True)

    def stop_element(self):
        tone_volume = 0.01
        length = 8
        silence_wave = array.array("H", [0] * length)
        for i in range(length):
            silence_wave[i] = int(tone_volume * (2 ** 15 - 1))
        silence_wave_sample = RawSample(silence_wave)
        mixer.voice[0].play(silence_wave_sample, loop=True)
        self.set_button(False)


# https://en.wikipedia.org/wiki/Simon_(game)#Gameplay
BLUE = Element("g4", (0, 0, 255), (1, -1))
YELLOW = Element("c4", (255, 255, 0), (-1, -1))
RED = Element("f4", (255, 0, 0), (1, 1))
GREEN = Element("g5", (0, 255, 0), (-1, 1))

ALL_ELEMENTS = [BLUE, YELLOW, RED, GREEN]


def element_for_key(key):
    return next(e for e in ALL_ELEMENTS if (key in e.all_keys))


import audiomixer

mixer = audiomixer.Mixer(voice_count=2, sample_rate=8000, channel_count=1,
                         bits_per_sample=16, samples_signed=False)


async def play_sequence(seq, speed_mult):
    for element in seq:
        element.start_element()
        await asyncio.sleep(0.5 * speed_mult)
        element.stop_element()
        await asyncio.sleep(0.1 * speed_mult)


class MemoryGame(Activity):
    accepting_user_input = False
    user_has_completed_current_sequence = False
    player_pos_in_seq = None
    seq = None
    game_over = False
    go_time_out = None

    def speed_mult(self):
        return 0.2 + math.pow(1.05, -len(self.seq))

    def reset_go_time_out(self):
        self.go_time_out = time.monotonic() + (self.speed_mult()*4)

    async def start(self):
        with audiobusio.I2SOut(board.GP0, board.GP1, board.INT) as audio:
            audio.play(mixer)

            for element in ALL_ELEMENTS:
                element.set_button(False)

            while True:
                self.seq = []
                self.game_over = False
                while not self.game_over:
                    self.seq.append(random.choice(ALL_ELEMENTS))
                    sp = self.speed_mult()
                    await asyncio.sleep(sp)
                    await play_sequence(self.seq, sp)
                    self.accepting_user_input = True
                    self.user_has_completed_current_sequence = False
                    self.player_pos_in_seq = 0
                    self.reset_go_time_out()

                    while not self.user_has_completed_current_sequence and not self.game_over:
                        if len(self.seq) > 1 and time.monotonic() > self.go_time_out:
                            self.game_over = True
                        await asyncio.sleep(0)
                    self.accepting_user_input = False

                failed_element = self.seq[self.player_pos_in_seq]
                for i in range(5):
                    failed_element.start_element()
                    await asyncio.sleep(0.1)
                    failed_element.stop_element()
                    await asyncio.sleep(0.1)

    def handle_key(self, event: keypad.Event, coords, single_key_stuff):
        if self.accepting_user_input:
            element = element_for_key(coords)
            if event.pressed:
                element.start_element()
            elif event.released:
                self.reset_go_time_out()
                element.stop_element()
                if self.seq[self.player_pos_in_seq] == element:
                    print("Right choice!")
                    self.player_pos_in_seq += 1
                    if self.player_pos_in_seq == len(self.seq):
                        self.user_has_completed_current_sequence = True
                else:
                    print("BAD choice!")
                    self.game_over = True
