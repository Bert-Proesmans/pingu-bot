import sys
import logging
import importlib
from types import ModuleType

import discord
from discord.ext import commands
from unidecode import unidecode

from bot import PinguBot

from .players import PlayerBase, UnknownPlayerError, ControlBase
from .players.stub import StubSource

log = logging.getLogger(__name__)


class NoVoiceStateError(discord.ClientException):
    pass


class NoPlayerError(discord.ClientException):
    pass


class Voice:
    """Commands for attaching the bot to voice channels"""

    def __init__(self, bot, players: dict):
        self.bot = bot
        self._voice_states = {}
        self._players = players

    @staticmethod
    def register_player(bot: PinguBot, name: str, player_module):
        if not isinstance(player_module, ModuleType):
            raise ValueError('player_module')
        cogs = bot.get_loaded_cogs_for_module(player_module)
        if not len(cogs) == 1:
            raise ValueError('Need class spawning AudioSource objects!')
        control_instance = cogs[0]
        if not isinstance(control_instance, ControlBase): raise ValueError('Not a control object')
        # Store the spawn_source object as callback for later use
        return name, control_instance.spawn_source

    def _get_voice_state(self, guild: discord.Guild):
        state = self._voice_states.get(guild.id, None)
        if not state:
            raise NoVoiceStateError()

        return state

    async def _remove_voice_state(self, guild: discord.Guild):
        state = self._voice_states.pop(guild.id, None)
        if not state:
            raise NoVoiceStateError()

        await state.disconnect()

    async def _build_voice_state_or_move(self, channel: discord.VoiceChannel):
        if not channel:
            raise ValueError('channel is None')

        guild_id = channel.guild.id
        try:
            client = await channel.connect()
            # Add stub player to voice state
            client.play(StubSource())
            # Pause the player.. now we can freely interchange sources within
            # the player (within the voice state)
            client.pause()
            self._voice_states[guild_id] = client
        except discord.ClientException:
            await self._voice_states[guild_id].move_to(channel)

        return self._voice_states[guild_id]

    async def _attach_source(self, guild: discord.Guild, player_str: str):
        if not guild:
            raise commands.MissingRequiredArgument('guild')
        if not player_str:
            raise commands.MissingRequiredArgument('player')

        if player_str not in self._players:
            raise UnknownPlayerError()

        player_builder = self._players[player_str]
        player = player_builder(guild=guild)
        # The following also tests against None
        if not isinstance(player, PlayerBase):
            raise Exception()

        state = self._get_voice_state(guild)
        was_playing = state.is_playing()
        # State auto pauses and resumes
        state.source = player
        if not was_playing:
            state.pause()

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx, *, channel: str):
        """Joins a voice channel."""
        all_channels = ctx.guild.voice_channels
        target_channel = next(
            filter(lambda x: unidecode(x.name).strip().startswith(channel), all_channels),
            None)
        try:
            await self._build_voice_state_or_move(target_channel)
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
            return

        try:
            await self._build_voice_state_or_move(summoned_channel)
        except discord.InvalidArgument:
            await ctx.send('This is not a voice channel...')
        except discord.ClientException:
            await ctx.send('Already in a voice channel...')

    @commands.command()
    @commands.guild_only()
    async def leave(self, ctx):
        """Stops playing music and the bot will leave the voice channel."""
        await self._remove_voice_state(ctx.guild)

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx):
        """Instructs the music player to send music to discord"""
        try:
            state = self._get_voice_state(ctx.guild)
            if state.source:
                state.source.resume()
                state.resume()
        except NoVoiceStateError:
            await ctx.send('I\'m not currently in a voice channel')

    @commands.command()
    @commands.guild_only()
    async def playing(self, ctx):
        """Shows info about the currently played song."""
        try:
            state = self._get_voice_state(ctx.guild)
            await ctx.send(f'Currently playing: {state.source}')
        except NoVoiceStateError:
            await ctx.send('I\'m not in a voice channel currently')

    @commands.command()
    @commands.guild_only()
    async def attach(self, ctx, source: str):
        """Attaches the specified player to the current voice state"""
        try:
            await self._attach_source(ctx.guild, source)
            await ctx.send(f'The source `{source}` succesfully attached!')
        except UnknownPlayerError:
            await ctx.send(f'The source `{source}` doesn\'t exist!')
        except NoVoiceStateError:
            await ctx.send('I\'m not in a voice channel currently')
        except:
            await ctx.send('Encountered an issue while building a `{player}` source..')


def setup(bot):
    """Setup handlers in this module for the provided bot."""
    log.info('Loading whitelisted players..')
    players_whitelist = bot.config.PLAYERS_WHITELIST
    players = {}
    for player in set(players_whitelist.keys()):
        player_module = players_whitelist[player]
        try:
            bot.load_extension(player_module)
            try:
                player_lib = bot.extensions[player_module]
                name, builder = Voice.register_player(bot, player, player_lib)
                players[name] = builder
            except:
                bot.unload_extension(player_module)
        except (discord.ClientException, ImportError):
            log.exception(f'Failed to load player `{player}`')

    voice_ext = Voice(bot, players)
    bot.add_cog(voice_ext)
