import logging
import tempfile
import os
import time

from discord.ext import commands

from bot import MissingSubCommandError
from cogs.players.player_base import ControlBase

from .spawn import SpotSpawn

log = logging.getLogger(__name__)


class SpotControl(ControlBase):
    def __init__(self, cfg=None):
        self._spawns = {}
        if cfg:
            self.config = cfg

    def spawn_source(self, *args, **kwargs):
        guild = kwargs.pop('guild', None)
        if not guild: raise ValueError('guild arg is missing')
        cred = self.config['tmp_credentials']
        spawn = SpotSpawn((cred['username'], cred['password']))
        self._spawns[guild.id] = spawn
        return spawn

    @commands.group(name='spotify')
    @commands.guild_only()
    async def _spotify(self, ctx):
        if not ctx.subcommand_passed:
            raise MissingSubCommandError()

    @_spotify.command(name='setup')
    @commands.guild_only()
    async def _setup(self, ctx):
        """Process for retrieving necessary credentials to log in with Spotify"""
        pass


def setup(bot):
    cfg = bot.config.SPOT_PLAYER
    spot_instance = SpotControl(cfg)
    bot.add_cog(spot_instance)


def teardown():
    """Optional: Can be used to clean up after usage."""
    pass
