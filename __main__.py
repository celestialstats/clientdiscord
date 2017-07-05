"""The main entrypoint for clientdiscord."""

import sys
import datetime
import logger
import discord
import os
import argparse
import pika
import json
import textwrap

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
parser.add_argument(
    '--rmq-username',
    default=os.environ.get('RMQ_USERNAME'),
    metavar='RMQ_USERNAME',
    help='RabbitMQ Username'
)
parser.add_argument(
    '--rmq-password',
    default=os.environ.get('RMQ_PASSWORD'),
    metavar='RMQ_PASSWORD',
    help='RabbitMQ Password'
)
parser.add_argument(
    '--rmq-exchange-name',
    default=os.environ.get('RMQ_EXCHANGE_NAME'),
    metavar='RMQ_EXCHANGE_NAME',
    help='RabbitMQ Exchange for Incoming Logs'
)
parser.add_argument(
    '--rmq-hostname',
    default=os.environ.get('RMQ_HOSTNAME'),
    metavar='RMQ_HOSTNAME',
    help='RabbitMQ Hostname'
)
parser.add_argument(
    '--rmq-port',
    default=os.environ.get('RMQ_PORT'),
    metavar='RMQ_PORT',
    help='RabbitMQ Port'
)

connection = None
channel = None
client = None


def main(args=None):
    """The main entrypoint for clientdiscord.

    :param args: The command line arguments."""
    global client
    __version__ = "0.1"
    if args is None:
        args = sys.argv[1:]
    args = parser.parse_args()

    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.

    LOGGER.info('Started Celestial Stats Discord Client v%s', __version__)
    LOGGER.info('Current System Time: %s', datetime.datetime.now().isoformat())

    def on_rmq_open(i_connection):
        print('Open')
        global connection
        connection = i_connection
        connection.channel(on_rmq_channel_open)

    def on_rmq_channel_open(i_channel):
        print('Channel')
        global channel
        global client
        channel = i_channel
        client.run(args.bot_token)

    client = discord.Client()

    @client.event
    async def on_ready():
        LOGGER.info('Connected to Discord: %s (ID: %s)', client.user.name,
                    client.user.id)

    @client.event
    async def on_message(message):
        utc_ts = message.timestamp.replace(tzinfo=datetime.timezone.utc)
        utc_ts = utc_ts.timestamp()
        LOGGER.info(
            '{}\\{} - {}: {}'.format(
                message.server.name,
                message.channel.name,
                message.author.display_name,
                textwrap.shorten(
                    message.content,
                    width=80,
                    placeholder="[...]"
                )
            )
        )
        channel.basic_publish(
            exchange=args.rmq_exchange_name,
            routing_key='',
            properties=pika.BasicProperties(
                headers={'chat-type': 'discord'}
            ),
            body=json.dumps({
                'SnowflakeID': int(message.id),
                'AuthorID': int(message.author.id),
                'AuthorDisplayName': message.author.display_name,
                'AuthorUsername': '%s#%s' % (message.author.name,
                                             message.author.discriminator),
                'ChannelID': int(message.channel.id),
                'ChannelName': message.channel.name,
                'Content': message.content,
                'ServerID': int(message.server.id),
                'ServerName': message.server.name,
                'Timestamp': float(utc_ts),
                'Type': 'MESSAGE',
            })
        )

    connection = pika.SelectConnection(
        parameters=pika.ConnectionParameters(
            args.rmq_hostname,
            int(args.rmq_port),
            '/',
            pika.PlainCredentials(args.rmq_username, args.rmq_password)
        ),
        on_open_callback=on_rmq_open
    )

    connection.ioloop.start()


if __name__ == "__main__":
    main()
