import array
import math
from audiocore import RawSample

PITCHES = "c,c#,d,d#,e,f,f#,g,g#,a,a#,b".split(",")


def note_freq(name: str) -> float:
    octave = int(name[-1])
    pitch = PITCHES.index(name[:-1].lower())
    return 440 * 2 ** ((octave - 4) + (pitch - 9) / 12.)


def tone_sample(tone_volume: float, frequency_hz: float) -> RawSample:
    length = math.floor(8000 / frequency_hz)
    sine_wave = array.array("H", [0] * length)
    for i in range(length):
        sine_wave[i] = int((1 + math.sin(math.pi * 2 * i / length)) * tone_volume * (2 ** 15 - 1))
    return RawSample(sine_wave)


def silence_sample() -> RawSample:
    length = 8
    silence_wave = array.array("H", [0] * length)
    for i in range(length):
        silence_wave[i] = 0
    return RawSample(silence_wave)
