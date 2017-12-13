import logging
import os
import tempfile

from discord.ext import commands

import librespot

from cogs.players import PlayerBase

log = logging.getLogger(__name__)


class SpotSpawn(PlayerBase):
    def __init__(self, pipe_path, pipe, credentials):
        self.pipe_path = pipe_path
        self.pipe = pipe
        self.session = librespot.Session.connect(credentials[0], credentials[1], pipe_path).wait()

    def read(self):
        pass

    def is_opus(self):
        return False

    def cleanup(self):
        try:
            self.pipe.close()
            os.remove(self.pipe_path)
        except:
            pass

    def skip(self, amount: int):
        pass

    def previous(self, amount: int):
        pass

    def play(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass
