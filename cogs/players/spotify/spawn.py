import logging

from discord.ext import commands

import librespot

from cogs.players import PlayerBase

log = logging.getLogger(__name__)

username = 'TODO'
password = 'TODO'

class SpotSpawn(PlayerBase):
	def __init__(self):
		self.session = librespot.Session.connect(username, password).wait()
        self.play()

