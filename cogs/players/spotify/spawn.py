import logging
import os
import tempfile

import numpy as np
from discord.ext import commands
import nnresample

import librespot

from cogs.players import PlayerBase

log = logging.getLogger(__name__)

FRAME_LENGTH = 20  # milliseconds
CHANNELS = 2
SAMPLE_SIZE = 2  # 2 bytes per sample (shorts)
INPUT_RATE = 44100
OUTPUT_RATE = 48000
QUALITY = 5

FRAME_20MS_44100 = int(((INPUT_RATE * FRAME_LENGTH) / 1000) * CHANNELS * SAMPLE_SIZE)
DT = np.dtype(np.int16).newbyteorder('<')


class SpotSpawn(PlayerBase):
    def __init__(self, pipe_file, credentials):
        self.pipe = pipe_file
        self.session = librespot.Session.connect(credentials[0], credentials[1], pipe_file).wait()
        self.player = self.session.player()
        self.playing = None
        self.is_playing = False

    def read(self):
        if self.is_playing and self.playing.poll():
            buf = self.pipe.read(FRAME_20MS_44100)
            if len(buf) == 0:
                return b''

            a = np.frombuffer(buf, dtype=DT)
            i = a.reshape((2, -1), order='F')
            resampled = nnresample.resample(i, OUTPUT_RATE, INPUT_RATE, axis=1, fc='nn', As=80, N=32001)
            o = resampled.reshape((-1,), order='F')
            return o.astype(DT).tobytes()

        return b''

    def is_opus(self):
        return False

    def cleanup(self):
        try:
            self.pipe.close()
        except:
            pass

    def skip(self, amount: int):
        pass

    def previous(self, amount: int):
        pass

    def queue(self, arg: str):
        track_prefix = 'track:'
        if arg.startswith(track_prefix):
            track = librespot.SpotifyId(arg[len(track_prefix):])
            self.playing = self.player.load(track)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        pass
