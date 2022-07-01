import board
import audiobusio
import audiomp3

# audio = audiobusio.I2SOut(board.GP0, board.GP1, board.INT)
# audio = audiobusio.I2SOut(board.GP0, board.GP1, board.INT)

# mp3 = audiomp3.MP3Decoder(open("tardis/IAmTheDoctor.Part1.40kbps.mp3", "rb"))
# print(f"mp3= {mp3}")
# audio.play(mp3)
#
# # This allows you to do other things while the audio plays!
# while audio.playing:
#     print(f"samples_decoded = {mp3.samples_decoded}")
#     pass


def play_music():

    mp3 = audiomp3.MP3Decoder(open("tardis/IAmTheDoctor.Part1.40kbps.mp3", "rb"))
    print(f"mp3= {mp3}")
    # audio.play(mp3)
    with audiobusio.I2SOut(board.GP0, board.GP1, board.INT) as a:
        a.play(mp3)
    print(f"Playing should have started, right?")
    # while audio.playing:
    #     print(f"samples_decoded = {mp3.samples_decoded}")
    #     pass
