import logging

import discord
from discord.ext import commands
from unidecode import unidecode

log = logging.getLogger(__name__)


class VoiceState:
    """Object for querying information about a certain voice connected client."""

    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

    @property
    def current(self):
        """Currently playing."""
        return None

    def skip(self, amount: int):
        """Skip `amount` of songs."""
        pass

    def previous(self, amount: int):
        """Go back `amount` of songs."""
        pass

    def play(self):
        """Send music to channel."""
        pass

    def pause(self):
        """Pause sending music to channel."""
        pass

    def stop(self):
        """Cancel playing music and free allocated resources."""
        pass


class Voice:
    """Commands for attaching the bot to voice channels"""

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def _get_voice_state(self, guild: discord.Guild):
        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[guild.id] = state

        return state

    async def _create_voice_client(self, channel: discord.VoiceChannel):
        if channel is None: raise discord.InvalidArgument('voice channel')

        client = await channel.connect()
        state = self._get_voice_state(channel.guild)
        state.voice_client = client

    async def _remove_voice_client(self, guild: discord.Guild):
        if guild is None: raise discord.InvalidArgument('guild')

        state = self.voice_states.pop(guild.id, None)
        if state is None:
            return

        if state.current:
            state.stop()

        try:
            if state.voice_client:
                await state.voice_client.disconnect()
        except:
            pass

    async def _move_voice_client(self, channel: discord.VoiceChannel):
        if channel is None: raise discord.InvalidArgument('voice channel')
        guild = channel.guild
        state = self._get_voice_state(guild)
        await state.voice_client.move_to(channel)

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


def setup(bot):
    """Setup handlers in this module for the provided bot."""
    bot.add_cog(Voice(bot))
