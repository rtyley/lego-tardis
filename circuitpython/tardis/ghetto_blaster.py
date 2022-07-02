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

class Command(object):
    def execute(self, audio):
        raise NotImplementedError("Please Implement this method")


class Play(Command):
    def __init__(self, mp3_file):
        self.mp3 = audiomp3.MP3Decoder(open(mp3_file, "rb"))

    def execute(self, audio):
        audio.play(self.mp3)


class Pause(Command):
    def execute(self, audio):
        audio.pause()


class Resume(Command):
    def execute(self, audio):
        audio.resume()


class Controls:
    def __init__(self):
        self._latest_command = None

    def make_request_for(self, command):
        self._latest_command = command

    def latest_command(self):
        command = self._latest_command
        self._latest_command = None
        return command


PlayIAmTheDoctor = Play("tardis/IAmTheDoctor.Part1.40kbps.mp3")


async def poll_for_music_requests(controls):
    with audiobusio.I2SOut(board.GP0, board.GP1, board.INT) as audio:
        while True:
            command = controls.latest_command()
            if command is not None:
                command.execute(audio)
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
