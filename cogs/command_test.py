import logging
import asyncio

from discord.ext import commands

log = logging.getLogger(__name__)


@commands.command(pass_context=True, no_pm=False)
async def echo(ctx, *args: str):
    """Echo received messages."""
    async with ctx.channel.typing():
        await asyncio.sleep(2.5)
        result_string = ' '.join(args)
        await ctx.send(result_string)
        log.debug(f'Echoed {result_string}')

@commands.command(pass_context=True, no_pm=True)
async def kill_bot(ctx):
    await ctx.send('Shutting down bot')
    await ctx.bot.logout()
    raise KeyboardInterrupt('Kill command received!')

def setup(bot):
    """Setup handlers in this module for the provided bot."""
    bot.add_command(echo)
    bot.add_command(kill_bot)
