#!/usr/bin/env python
"""The main entrypoint for clientdiscord."""

import sys
import datetime
import logger
import discord
import os
import argparse

from argparse import RawTextHelpFormatter

LOGGER = logger.get_logger(__name__)
parser = argparse.ArgumentParser(
    description='Celestial Stats strives to the premier platform for chat \
statistics. Any platform. Any statistic. This is the Discord client \
for listening to Discord server activity.\n\nIn place of command line \
arguments you may use environmental variables named in CAPS.',
    formatter_class=RawTextHelpFormatter
)
parser.add_argument(
    '--client-id',
    default=os.environ.get('DISCORD_CLIENTID'),
    metavar='DISCORD_CLIENTID',
    help='Discord Client ID'
)
parser.add_argument(
    '--client-secret',
    default=os.environ.get('DISCORD_CLIENTSECRET'),
    metavar='DISCORD_CLIENTSECRET',
    help='Discord Client Secret'
)
parser.add_argument(
    '--bot-token',
    default=os.environ.get('DISCORD_BOTTOKEN'),
    metavar='DISCORD_BOTTOKEN',
    help='Discord Bot Token'
)


def main(args=None):
    """The main entrypoint for clientdiscord.

    :param args: The command line arguments."""
    __version__ = "0.1"
    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args()

    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.

    LOGGER.info("Started Celestial Stats Discord Client v" + __version__)
    LOGGER.info("Current System Time: " + datetime.datetime.now().isoformat())

    client = discord.Client()

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    client.run(args.bot_token)


if __name__ == "__main__":
    main()
