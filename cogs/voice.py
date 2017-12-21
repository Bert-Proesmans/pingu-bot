import sys
import logging
import importlib
from types import ModuleType

import discord
from discord.ext import commands
from unidecode import unidecode

from .players import PlayerBase, UnknownPlayerError, ControlBase

log = logging.getLogger(__name__)


class NoVoiceStateError(discord.ClientException):
    pass


class VoiceState:
    """Object for querying information about a certain voice connected client."""

    def __init__(self, bot):
        self.bot = bot
        self._voice_client = None
        self._player = None

    @property
    def current(self):
        """Currently playing. This method should always return a string!"""
        return str(self._player) or 'Nothing to play'

    @property
    def voice_client(self):
        return self._voice_client

    async def create_voice_client(self, channel: discord.VoiceChannel):
        if channel is None: raise commands.MissingRequiredArgument('voice channel')

        if self._voice_client:
            await self.move_voice_client(channel)
            return

        client = await channel.connect()
        self._voice_client = client

    async def remove_voice_client(self):
        if not self._voice_client:
            return

        if self._player:
            self._player.stop()

        try:
            await self._voice_client.disconnect()
        except:
            pass
        finally:
            self._voice_client = None

    async def move_voice_client(self, channel: discord.VoiceChannel):
        if channel is None: raise commands.MissingRequiredArgument('voice channel')
        if self._voice_client:
            await self._voice_client.move_to(channel)

    def set_player(self, player):
        if not isinstance(player, PlayerBase):
            raise Exception

        if self._player is not None:
            self._player.stop()

        self._player = player
        self._voice_client.play(self._player)
        self._player.play()


class Voice:
    """Commands for attaching the bot to voice channels"""

    def __init__(self, bot):
        self.bot = bot
        self._voice_states = {}
        self._players = {}

    def register_player(self, name: str, player_module):
        if not isinstance(player_module, ModuleType): raise ValueError('player_module')
        cogs = self.bot.get_loaded_cogs_for_module(player_module)
        if not len(cogs) == 1: raise ValueError('Need class spawning AudioSource objects!')
        control_instance = cogs[0]
        if not isinstance(control_instance, ControlBase): raise ValueError('Not a control object')
        # Store the spawn_source object as callback for later use
        self._players[name] = control_instance.spawn_source

    def _get_voice_state(self, guild: discord.Guild):
        state = self._voice_states.get(guild.id)
        if state is None:
            raise NoVoiceStateError()

        return state

    def _build_voice_state(self, guild: discord.Guild):
        state = self._voice_states.get(guild.id)
        if state is None:
            state = VoiceState(self)
            self._voice_states[guild.id] = state
        return state

    async def _attach_player(self, guild: discord.Guild, player_str: str):
        if not guild: raise commands.MissingRequiredArgument('guild')
        if not player_str: raise commands.MissingRequiredArgument('player')

        if player_str not in self._players:
            raise UnknownPlayerError()

        player_builder = self._players[player_str]
        player = player_builder(guild=guild)
        # The following also tests against None
        if not isinstance(player, PlayerBase):
            raise Exception()

        state = self._get_voice_state(guild)
        state.set_player(player)

    @commands.command()
    @commands.guild_only()
    async def join(self, ctx, *, channel: str):
        """Joins a voice channel."""
        all_channels = ctx.guild.voice_channels
        target_channel = next(
            filter(lambda x: unidecode(x.name).strip().startswith(channel), all_channels),
            None)
        try:
            state = self._build_voice_state(ctx.guild)
            await state.create_voice_client(target_channel)
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

        state = self._build_voice_state(summoned_channel.guild)
        await state.create_voice_client(summoned_channel)

    @commands.command()
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops playing music and the bot will leave the voice channel."""
        state = self._voice_states.pop(ctx.guild.id, None)
        if state:
            await state.remove_voice_client()

    @commands.command()
    @commands.guild_only()
    async def playing(self, ctx):
        """Shows info about the currently played song."""
        try:
            state = self._get_voice_state(ctx.guild)
            await ctx.send(f'Currently playing: {state.current}')
        except NoVoiceStateError:
            await ctx.send('I\'m not in a voice channel currently')

    @commands.command()
    @commands.guild_only()
    async def attach(self, ctx, player: str):
        """Attaches the specified player to the current voice state"""
        try:
            await self._attach_player(ctx.guild, player)
        except UnknownPlayerError:
            await ctx.send(f'The player `{player}` doesn\'t exist!')
        except NoVoiceStateError:
            await ctx.send('I\'m not in a voice channel currently')
        except:
            await ctx.send('Encountered an issue while building a `{player}` player..')


def setup(bot):
    """Setup handlers in this module for the provided bot."""
    voice_ext = Voice(bot)
    bot.add_cog(voice_ext)

    log.info('Loading whitelisted players..')
    players_whitelist = bot.config.PLAYERS_WHITELIST
    for player in set(players_whitelist.keys()):
        player_module = players_whitelist[player]
        try:
            bot.load_extension(player_module)
            try:
                player_lib = bot.extensions[player_module]
                voice_ext.register_player(player, player_lib)
            except:
                bot.unload_extension(player_module)
        except (discord.ClientException, ImportError):
            log.exception(f'Failed to load player `{player}`')
