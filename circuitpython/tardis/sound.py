import board
import audiobusio
import audiomp3

i2c = board.I2C()

audio = audiobusio.I2SOut(board.GP0, board.GP1, board.INT)

mp3 = audiomp3.MP3Decoder(open("IAmTheDoctor.Part1.40kbps.mp3", "rb"))
audio.play(mp3)

# This allows you to do other things while the audio plays!
while audio.playing:
    pass