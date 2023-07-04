import board
from . import I2SPins


class KeyBow2040I2SPins(I2SPins):
    def __init__(self):
        self.bit_clock = board.GP0
        self.word_select = board.GP1
        self.data = board.INT
