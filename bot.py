import logging
import sys
import traceback
import datetime
import asyncio

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


def _prefix_callable(bot, msg):
    bot_id = bot.user.id
    allowed_prefix = [f'<@!{bot_id}> ', f'<@{bot_id}> ']
    if msg.guild is None:
        allowed_prefix.append('!')
        allowed_prefix.append('?')
    else:
        allowed_prefix.extend(bot.get_prefixes_for_guild(msg.guild.id))
    # DBG
    log.debug(allowed_prefix)
    return allowed_prefix


class PinguBot(commands.Bot):
    """Wrapper class to support the Pingu Bot"""

    def __init__(self, cache_manager):
        super().__init__(command_prefix=_prefix_callable,
                         description=self.config.BOT_DESCRIPTION,
                         pm_help=True)
        self.global_cache = None
        self._cache_manager = cache_manager
        self._setup_extensions()

    def _setup_extensions(self):
        for extension in self.config.EXTENSIONS_WHITELIST:
            try:
                self.load_extension(extension)
            except Exception as e:
                log.exception(f'Failed to load extension `{extension}`')
                traceback.print_exc()

    @property
    def config(self):
        return __import__('config')

    @property
    def cache_manager(self):
        return self._cache_manager

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
        # Update bot username and avatar
        if self.user.name != self.config.BOT_NICKNAME:
            await self.user.edit(username=self.config.BOT_NICKNAME)
            # TODO Maybe update the avatar as well?

        log.info(f'Ready: {self.user} (ID: {self.user.id})')

    async def on_resumed(self):
        log.info('resumed...')

    def run(self):
        # Remove a reference to the cache manager, because COGS should operate on cache arena's.
        self.global_cache = self._cache_manager.global_cache
        del self._cache_manager
        # Connect and run the event-loop of our bot
        super().run(self.config.TOKEN, reconnect=True)

    async def close(self):
        log.info('Bot close requested')
        super().close()

    def get_prefixes_for_guild(self, guild_id: int):
        prefix_key = 'prefix_' + str(guild_id)
        try:
            prefixes = self.global_cache[prefix_key]
        except KeyError:
            prefixes = []
            self.global_cache[prefix_key] = prefixes
        return prefixes

    async def respond_editable(self, message: discord.Message, response: str, previous_message=None):
        if previous_message is None:
            previous_message = await message.channel.send(response)
        else:
            await previous_message.edit(response)

        await self._check_edit(message, previous_message.content)

    async def _check_edit(self, message: discord.Message, sent_response: discord.Message):
        """NON ROBUST scheme for checking edited messages"""
        original_content = message.content
        for _ in range(30):
            if message.content != original_content:
                # TODO Introduce seperate method which also incorporates the previous message contents
                await self.on_message(message.content)
                return
            await asyncio.sleep(1)
