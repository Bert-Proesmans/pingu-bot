import logging
import sys
import traceback
import datetime

from discord.ext import commands

_description = """
NOOT NOOT! Development Pingu bot!
"""

_bot_nickname = "b-dev Pingu Bot"

log = logging.getLogger(__name__)

whitelisted_extensions = (
    'cogs.command_test',
)


def _prefix_callable(bot, msg):
    bot_id = bot.user.id
    allowed_prefix = [f'<@!{bot_id}> ', f'<@{bot_id}> ']
    if msg.guild is None:
        allowed_prefix.append('!')
        allowed_prefix.append('?')
    else:
        # allowed_prefix.extend(bot.prefixes.get(msg.guild.id, ['?', '!']))
        pass
    # DBG
    log.debug(allowed_prefix)
    return allowed_prefix


class PinguBot(commands.Bot):
    """Wrapper class to support the Pingu Bot"""

    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, description=_description, pm_help=True)
        self._setup_extensions()

    def _setup_extensions(self):
        for extension in whitelisted_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                log.exception(f'Failed to load extension `{extension}`')
                traceback.print_exc()

    @property
    def config(self):
        return __import__('config')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            log.exception(f'{error.original.__class__.__name__}: {error.original}')
        # Extend functionality here for other kinds of issues

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        log.info(f'Ready: {self.user} (ID: {self.user.id})')
        # TODO: change nickname of bot

    async def on_resumed(self):
        log.info('resumed...')

    def run(self):
        super().run(self.config.TOKEN, reconnect=True)

    async def close(self):
        log.info('Bot close requested')
        super().close()

