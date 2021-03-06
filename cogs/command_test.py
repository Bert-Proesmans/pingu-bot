import logging
import asyncio

from discord.ext import commands

log = logging.getLogger(__name__)


class TestCommands:
    """Bot testing commands"""

    def __init__(self, bot):
        self.bot = bot
        self._setup()

    def _setup(self):
        pass

    @commands.command()
    @commands.is_owner()
    async def echo(self, ctx, *args: str):
        """Echo received messages."""
        async with ctx.channel.typing():
            await asyncio.sleep(2.5)
            result_string = ' '.join(args)
            await ctx.send(result_string)
            log.debug(f'Echoed {result_string}')

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """The bot will be logged out and the session will end."""
        await ctx.send('Shutting down bot')
        await self.bot.logout()
        # Logout is implicit through interrupt
        # Do NOT explicitly stop the event loop!
        raise KeyboardInterrupt('Kill command received!')


def setup(bot):
    """Setup handlers in this module for the provided bot."""
    bot.add_cog(TestCommands(bot))
