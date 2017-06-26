#!/usr/bin/env python
"""The main entrypoint for clientdiscord."""

import sys
import datetime
import logger
import discord
import os
import argparse
import boto3
import uuid

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
    '--aws-default-region',
    default=os.environ.get('AWS_DEFAULT_REGION'),
    metavar='AWS_DEFAULT_REGION',
    help='AWS Default Region'
)
parser.add_argument(
    '--aws-access-key-id',
    default=os.environ.get('AWS_ACCESS_KEY_ID'),
    metavar='AWS_ACCESS_KEY_ID',
    help='AWS Access Key Id'
)
parser.add_argument(
    '--aws-secret-access-key',
    default=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    metavar='AWS_SECRET_ACCESS_KEY',
    help='AWS Secret Access Key'
)
parser.add_argument(
    '--log-table-name',
    default=os.environ.get('LOG_TABLE_NAME'),
    metavar='LOG_TABLE_NAME',
    help='AWS DynamoDB Table Name for Incoming Logs'
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

    session = boto3.Session(
        aws_access_key_id=args.aws_access_key_id,
        aws_secret_access_key=args.aws_secret_access_key,
        region_name=args.aws_default_region,
    )

    ddb = session.client('dynamodb')
    ddb.put_item(
        TableName=args.log_table_name,
        Item={
            'LogUuid': {'S': uuid.uuid4().hex},
            'AuthorID': {'N': '108030288910729216'},
            'ChannelID': {'N': '108030304773586944'},
            'Content': {'S': 'Man bloodbourne is confusing.'},
            'ServerID': {'N': '108030304773586944'},
            'ServerType': {'S': 'DISCORD'},
            'Timestamp': {'N': '1497924425357'},
            'Type': {'S': 'MESSAGE'},
        }
    )

    """
    client = discord.Client()

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    @client.event
    async def on_message(message):
        print(message)

    client.run(args.bot_token)
    """

if __name__ == "__main__":
    main()
