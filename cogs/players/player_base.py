
# TODO Implement UnknownPlayerError

class PlayerBase:
    def skip(self, amount: int):
        """Skip `amount` of songs."""
        raise NotImplementedError

    def previous(self, amount: int):
        """Go back `amount` of songs."""
        raise NotImplementedError

    def play(self):
        """Send music to channel."""
        raise NotImplementedError

    def pause(self):
        """Pause sending music to channel."""
        raise NotImplementedError

    def stop(self):
        """Cancel playing music and free allocated resources."""
        raise NotImplementedError
