import board
import audiobusio
import audiomp3
import asyncio

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


class Controls:
    def __init__(self):
        self._play_request = None

    def make_request_for(self, req):
        self._play_request = req

    def latest_request(self):
        req = self._play_request
        self._play_request = None
        return req


async def poll_for_music_requests(controls):
    boo = audiomp3.MP3Decoder(open("tardis/IAmTheDoctor.Part1.40kbps.mp3", "rb"))
    with audiobusio.I2SOut(board.GP0, board.GP1, board.INT) as audio:
        while True:
            req = controls.latest_request()
            if req is not None:


                mp3 = boo  # audiomp3.MP3Decoder(open(req, "rb"))
                print(f"mp3= {mp3}")
                audio.play(mp3)
            await asyncio.sleep(0.05)

# def play_music():
#
#     mp3 = audiomp3.MP3Decoder(open("tardis/IAmTheDoctor.Part1.40kbps.mp3", "rb"))
#     print(f"mp3= {mp3}")
#     # audio.play(mp3)
#     with audiobusio.I2SOut(board.GP0, board.GP1, board.INT) as a:
#         a.play(mp3)
#     print(f"Playing should have started, right?")
#     # while audio.playing:
#     #     print(f"samples_decoded = {mp3.samples_decoded}")
#     #     pass
