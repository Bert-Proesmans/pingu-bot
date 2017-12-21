import logging

import numpy as np
import nnresample

from cogs.players import PlayerBase

log = logging.getLogger(__name__)

FRAME_LENGTH = 20  # milliseconds
CHANNELS = 2
SAMPLE_SIZE = 2  # 2 bytes per sample (shorts)
INPUT_RATE = 44100
OUTPUT_RATE = 48000
QUALITY = 5

FRAME_20MS_48000 = int(((OUTPUT_RATE * FRAME_LENGTH) / 1000) * CHANNELS * SAMPLE_SIZE)
DT = np.dtype(np.int16).newbyteorder('<')
ZEROS = np.zeros(FRAME_20MS_48000, dtype=DT).tobytes()


class StubSource(PlayerBase):
    """Source meant to initiate audio players when constructing voice clients."""

    def read(self):
        return ZEROS

    def skip(self, amount: int):
        pass

    def previous(self, amount: int):
        pass

    def resume(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def queue(self, arg: str):
        pass
