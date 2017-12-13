import logging

from discord.ext import commands

log = logging.getLogger(__name__)

class SpotControl:
    def __init__(self):
        self._spawns = {}
        self._credentials = {}
        

    def _build_spawn(self):
        """Build a state object to control the spun up librespot instance."""
        pass

    @commands.group(name='spotify')
    @commands.guild_only()
    async def _spotify(self, ctx):
        if not ctx.subcommand_passed:
            # TODO Just raise 'missing subcommand' error
            await ctx.send(t'You have to pass a subcommand.')

    @_spotify.command(name='setup')
    @commands.guild_only()
    async def _setup(self, ctx):
        """Process for retrieving necessary credentials to log in with Spotify"""
        pass


def setup(bot):
    spot_instance = SpotControl()
    bot.add_cog(spot_instance)

