import sys
import logging
import importlib

import discord
from discord.ext import commands
from unidecode import unidecode

from .players import PlayerBase
from .players.spotify import SpotControl as Spotify

log = logging.getLogger(__name__)

PLAYERS_WHITELIST = {
    'spotify': 'cogs.players.spotify',
}


class VoiceState:
    """Object for querying information about a certain voice connected client."""

    def __init__(self, bot):
        self.bot = bot
        self._voice_client = None
        self._player = None

    @property
    def current(self):
        """Currently playing."""
        return None

    @property
    def voice_client(self):
        return self._voice_client

    def set_player(self, player):
        if not isinstance(player, PlayerBase):
            raise Exception

        if self._player is not None:
            self._player.stop()

        self._player = player


class Voice:
    """Commands for attaching the bot to voice channels"""

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
        self._players = {}

    def _setup_players(self):
        for player in set(PLAYERS_WHITELIST.keys()):
            lib_path = PLAYERS_WHITELIST[player]
            lib = importlib.import_module(lib_path)
            if not hasattr(lib, 'setup'):
                del lib
                del sys.modules[player]
                log.error(f'{player} has NO setup method!')
            construction_delegate = lib.setup()
            self._players[player] = construction_delegate
            # TODO This delegate MUST be checked for return type!

    def _get_voice_state(self, guild: discord.Guild):
        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[guild.id] = state

        return state

    async def _create_voice_client(self, channel: discord.VoiceChannel):
        if channel is None: raise commands.MissingRequiredArgument('voice channel')

        client = await channel.connect()
        state = self._get_voice_state(channel.guild)
        state.voice_client = client

    async def _remove_voice_client(self, guild: discord.Guild):
        if guild is None: raise commands.MissingRequiredArgument('guild')

        state = self.voice_states.pop(guild.id, None)
        if state is None:
            return

        try:
            if state.current:
                state.stop()
            if state.voice_client:
                await state.voice_client.disconnect()
        except:
            pass

    async def _move_voice_client(self, channel: discord.VoiceChannel):
        if channel is None: raise commands.MissingRequiredArgument('voice channel')
        guild = channel.guild
        state = self._get_voice_state(guild)
        await state.voice_client.move_to(channel)

    async def _attach_player(self, guild: discord.Guild, player_str: str):
        if guild is None: raise commands.MissingRequiredArgument('guild')
        if player_str is None: raise commands.MissingRequiredArgument('player')

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx, *, channel: str):
        """Joins a voice channel."""
        all_channels = ctx.guild.voice_channels
        target_channel = next(
            filter(lambda x: unidecode(x.name).strip().startswith(channel), all_channels),
            None)
        try:
            await self._create_voice_client(target_channel)
        except discord.InvalidArgument:
            await ctx.send('This is not a voice channel...')
        except discord.ClientException:
            await ctx.send('Already in a voice channel...')

    @commands.command()
    @commands.guild_only()
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        author_state = ctx.message.author.voice
        summoned_channel = None
        if author_state is not None:
            summoned_channel = author_state.channel

        if summoned_channel is None:
            await ctx.send('You are not in a voice channel.')

        state = self._get_voice_state(summoned_channel.guild)
        if state.voice_client is None:
            state.voice_client = await summoned_channel.connect()
        else:
            await self._move_voice_client(summoned_channel)

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops playing music and the bot will leave the voice channel."""
        await self._remove_voice_client(ctx.guild)

    @commands.command()
    @commands.guild_only()
    async def playing(self, ctx):
        """Shows info about the currently played song."""
        state = self._get_voice_state(ctx.guild)
        if state.current is None:
            await ctx.send('Not playing anything.')
        else:
            await ctx.send(f'Currently playing: {state.current}')

    @commands.command()
    @commands.guild_only()
    async def attach(self, ctx, player: str):
        """Attaches the specified player to the current voice state"""
        try:
            await self._attach_player(ctx.guild, player)
        except commands.MissingRequiredArgument as e:
            ctx.send(f'Your command lacks the following argument: {e.param}')


def setup(bot):
    """Setup handlers in this module for the provided bot."""
    bot.add_cog(Voice(bot))
