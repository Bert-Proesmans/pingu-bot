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
        pipe_info = self._setup_pipe()
        # TODO Remove hardcoded credentials!
        cred = self.config.tmp_credentials
        spawn = SpotSpawn(pipe_info, (cred.username, cred.password))
        self._spawns[guild.id] = spawn
        return spawn

    def _setup_pipe(self):
        fd_read, fd_write = os.pipe()
        pipe_read = open(fd_read, 'rb')
        pipe_write = open(fd_write, 'wb')
        return pipe_read, pipe_write

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
