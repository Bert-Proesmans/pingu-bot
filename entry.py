import logging
import contextlib

import click

import util
from bot import PinguBot

@contextlib.contextmanager
def setup_logging():
    """Method available in `with` syntax to construct and destruct logging infrastructure."""
    try:
        # Setup logging
        # Print all errors and higher, for all modules, to console.
        logging.basicConfig(level=logging.ERROR)

        # Make sure to print ALL data from cogs
        logging.getLogger('cogs').setLevel(logging.DEBUG)

        # Send discord logging to file.
        logging.getLogger('discord').setLevel(logging.DEBUG)
        handler = util.ExistsFileHandler(filename='logs/discord.log', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logging.getLogger().addHandler(handler)

        yield
    finally:
        # Cleanup installed handlers
        root_log = logging.getLogger()
        handlers = root_log.handlers[:]  # Copies handler list
        for hldr in handlers:
            hldr.close()
            root_log.removeHandler(hldr)


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        with setup_logging():
            run_bot()


def run_bot():
    # Setup the bot, it will automatically use the discord logger.
    bot = PinguBot()
    # Start the bot
    bot.run()


if __name__ == "__main__":
    main()
