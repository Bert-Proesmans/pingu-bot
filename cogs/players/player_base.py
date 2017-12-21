from abc import ABC

import discord


class UnknownPlayerError(discord.ClientException):
    pass


class ControlBase(ABC):
    def spawn_source(self, *args, **kwargs):
        """Spawn a new audiosource object, which can be played."""
        raise NotImplementedError


class PlayerBase(ABC, discord.AudioSource):
    def read(self):
        """Returns 20ms worth of audio data; either PCM or Opus.
        The requested specs are stereo/interleaved/i16/48KHz
        """
        raise NotImplementedError

    def skip(self, amount: int):
        """Skip `amount` of songs."""
        raise NotImplementedError

    def previous(self, amount: int):
        """Go back `amount` of songs."""
        raise NotImplementedError

    def resume(self):
        """Send music to channel."""
        raise NotImplementedError

    def pause(self):
        """Pause sending music to channel."""
        raise NotImplementedError

    def stop(self):
        """Cancel playing music and free allocated resources."""
        raise NotImplementedError

    def queue(self, arg: str):
        """Add a certain player item to the queue"""
        raise NotImplementedError
