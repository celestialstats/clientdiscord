#!/usr/bin/env python
"""The main entrypoint for clientdiscord."""

import sys
import datetime
import logger
import discord
import os
import argparse
import json
import pika

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

    LOGGER.info('Started Celestial Stats Discord Client v%s', __version__)
    LOGGER.info('Current System Time: %s', datetime.datetime.now().isoformat())

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='192.168.1.180',
        port=5672,
        credentials=pika.PlainCredentials(username="SUPER_SECRET_USER_HERE", password="SUPER_SECRET_PASS_HERE")
    ))
    channel = connection.channel()
    client = discord.Client()

    @client.event
    async def on_ready():
        LOGGER.info('Connected to Discord: %s (ID: %s)', client.user.name,
                    client.user.id)

    @client.event
    async def on_message(message):
        utc_ts = message.timestamp.replace(tzinfo=datetime.timezone.utc)
        utc_ts = utc_ts.timestamp()
        item = {
            'SnowflakeID': {'N': message.id},
            'AuthorID': {'N': message.author.id},
            'AuthorDisplayName': {'S': message.author.display_name},
            'AuthorUsername': {'S': message.author.name + '#' +
                                    message.author.discriminator},
            'ChannelID': {'N': message.channel.id},
            'ChannelName': {'S': message.channel.name},
            'Content': {'S': message.content},
            'ServerID': {'N': message.server.id},
            'Timestamp': {'N': str(utc_ts)},
            'Type': {'S': 'MESSAGE'},
        }
        LOGGER.info(json.dumps(item))
        channel.basic_publish(exchange='incoming_logs',
                              routing_key='',
                              properties=pika.BasicProperties(headers={'chat-type': 'discord'}),
                              body=json.dumps(item))

    client.run(args.bot_token)


if __name__ == "__main__":
    main()
