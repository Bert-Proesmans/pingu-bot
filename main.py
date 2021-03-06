#!/usr/bin/env python3

import asyncio
import logging
import contextlib

import click
import discord

import util
from bot import PinguBot


@contextlib.contextmanager
def setup_logging():
    """Method available in `with` syntax to construct and destruct logging infrastructure."""
    try:
        # Setup logging
        # Print all errors and higher, for all modules, to console.
        logging.basicConfig(level=logging.ERROR)

        # Make sure to print ALL data from our bot class
        logging.getLogger('bot').setLevel(logging.DEBUG)
        logging.getLogger('cogs').setLevel(logging.DEBUG)
        logging.getLogger('util').setLevel(logging.DEBUG)

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


@contextlib.contextmanager
def setup_cache(cache_path):
    """Method available in `with` syntax to setup/tear down caching infrastructure."""
    cache_manager = None
    try:
        cache_manager = util.CacheManager(cache_path)
        yield cache_manager
    finally:
        cache_manager.cleanup()


@click.group(invoke_without_command=True)
@click.option('--tmp_path', default=None, help='Location of cache files.')
@click.pass_context
def main(ctx, tmp_path):
    if ctx.invoked_subcommand is None:
        # Attaches the event loop to this thread
        event_loop = asyncio.get_event_loop()
        with setup_logging(), setup_cache(tmp_path) as cache_manager:
            run_bot(cache_manager)


def run_bot(cache_manager):
    # Setup the bot, it will automatically use the discord logger.
    bot = PinguBot(cache_manager)

    # Make sure everything is setup to join/send data to voice channels.
    if bot.config.ENABLE_VOICE:
        logging.getLogger('bot').info('Loading OPUS')
        if not discord.opus.is_loaded():
            discord.opus.load_opus('opus')

    # Start the bot
    bot.run()


if __name__ == "__main__":
    main()
