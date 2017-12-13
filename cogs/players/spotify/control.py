import logging

from discord.ext import commands

from bot import MissingSubCommandError
from cogs.players.player_base import ControlBase

log = logging.getLogger(__name__)


class SpotControl(ControlBase):
    def __init__(self):
        self._spawns = {}
        self._credentials = {}

    def spawn_source(self, *args, **kwargs):
        pass

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
