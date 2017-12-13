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
    def __init__(self):
        self._spawns = {}

    def spawn_source(self, *args, **kwargs):
        guild = kwargs.pop('guild', None)
        if not guild: raise ValueError('guild arg is missing')
        (path, pipe) = self._setup_named_pipe()
        # TODO Remove hardcoded credentials!
        spawn = SpotSpawn(path, pipe, ('todo', 'todo'))
        self._spawns[guild.id] = spawn
        return spawn

    def _setup_named_pipe(self):
        pipe_name = 'pipe-spot-' + str(time.time())
        pipe_path = os.path.join(tempfile.tempdir(), pipe_name)
        os.mkfifo(pipe_path)
        pipe_file = open(pipe_path, 'rb')
        return pipe_path, pipe_file

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
    spot_instance = SpotControl()
    bot.add_cog(spot_instance)


def teardown():
    """Optional: Can be used to clean up after usage."""
    pass
