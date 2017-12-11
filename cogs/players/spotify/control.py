import logging

from discord.ext import commands

import librespot

from cogs.players import PlayerBase

log = logging.getLogger(__name__)

username = 'TODO'
password = 'TODO'


class SpotControl(PlayerBase):
    """Manage playing spotify songs through voice channels"""

    def __init__(self):
        log.info("Spotify-Control started")
        self.session = librespot.Session.connect(username, password).wait()
        self.play()

    def skip(self, amount: int):
        pass

    def previous(self, amount: int):
        pass

    def play(self):
        log.info("Starting to play")
        player = self.session.player()
        player.play()

    def pause(self):
        pass

    def stop(self):
        pass


def setup():
    def init_player():
        return SpotControl()

    return init_player
