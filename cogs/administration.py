import logging
import asyncio

from discord.ext import commands

log = logging.getLogger(__name__)


class Administration:
    """Commands for manipulating the bot itself. Much META, such WOW."""

    def __init__(self, bot):
        self.bot = bot
        self._setup()

    def _setup(self):
        pass

    @commands.group(name='add')
    async def _add(self, ctx):
        if not ctx.subcommand_passed:
            await ctx.send(f'You have to pass a subcommand. Type \'{ctx.prefix} help\' for more info.')
        else:
            await ctx.send(f'[DBG] {ctx.subcommand_passed}')

    @commands.group(name='remove')
    async def _remove(self, ctx):
        if not ctx.subcommand_passed:
            await ctx.send(f'You have to pass a subcommand. Type \'{ctx.prefix} help\' for more info.')
        else:
            await ctx.send(f'[DBG] {ctx.subcommand_passed}')

    @_add.command(name='prefix')
    @commands.cooldown(2, 5.0, commands.BucketType.guild)
    @commands.guild_only()
    async def _add_prefix(self, ctx, prefix):
        """Add a prefix for which this bot will listen to."""
        self.bot.add_prefix_for_guild(ctx.guild.id, prefix)
        await ctx.send(f'Added `{prefix}` to usable prefixes')

    @_remove.command(name='prefix', aliases=[])
    @commands.cooldown(2, 5.0, commands.BucketType.guild)
    @commands.guild_only()
    async def _remove_prefix(self, ctx, prefix):
        """Remove a prefix for which this bot currently listens to."""
        # TODO
        pass


def setup(bot):
    """Setup handlers in this module for the provided bot."""
    bot.add_cog(Administration(bot))
