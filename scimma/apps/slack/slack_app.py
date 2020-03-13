#!/usr/bin/env python

__author__ = "Shereen Elsayed (s_elsayed@ucsb.edu)"
__description__ = "Post received messages to Slack channel"

import argparse
import configparser
import requests
import json
import sys
from genesis import streaming as stream


def _add_parser_args(parser):
    """
        Parse arguments for broker, configurations and options
    """

    parser.add_argument(
        "-b",
        "--broker-url",
        required=True,
        help="Sets the broker URL (kafka://host[:port]/topic) to publish GCNs to.",
    )

    # Configuration options
    config = parser.add_mutually_exclusive_group()
    config.add_argument(
        "-F", "--config-file", help="Set client configuration from file.",
    )
    config.add_argument(
        "-X",
        "--config",
        action="append",
        help="Set client configuration via prop=val. Can be specified multiple times.",
    )

    # Subscription option
    parser.add_argument(
        "-j", "--json", help="Request gcn output as raw json",
        action='store_true',
    )
    parser.add_argument(
        "-e", "--earliest", help="Request to stream from the earliest available Kafka offset",
        action='store_true',
    )
    parser.add_argument(
        "-t", "--timeout", help="Specifies the time (in seconds) to wait for new messages.",
    )

    # Slack configuration File
    parser.add_argument(
        "-S",
        "--slack-config-file",
        required=True,
        help="set Slack configuration from file ",
    )


def parse_slack_config_file(slack_config_file):
    """
        Description:
            Parse slack configuration file

        Args:
            slack_config_file: Path to slack configuration file

        Returns:
            Dictionary with slack configurations
    """

    config = configparser.ConfigParser()
    slack_config_dict  = {}
    try:
        config.read(slack_config_file)
        slack_config_dict = {
            'slack_token': config['SLACK_PROPERTIES']['SLACK_TOKEN'],
            'slack_username': config['SLACK_PROPERTIES']['SLACK_USERNAME'],
            'slack_icon_url': config['SLACK_PROPERTIES']['SLACK_ICON_URL'],
            'topic_channel_mapping': {},
            'default_channel': config['GENERAL']['DEFAULT_CHANNEL']}

        for key in config['TOPIC_CHANNEL_MAPPING']:
            slack_config_dict['topic_channel_mapping'][key] = config['TOPIC_CHANNEL_MAPPING'][key]
    
    except IOError:
        print("Error: Slack configuration file does not appear to exist.")
        sys.exit(1)
    except configparser.NoSectionError as err:
        print("Error: A section is missing. {0}".format(err))
        sys.exit(1)
    except configparser.DuplicateSectionError as err:
        print("Error: Section duplication error. {0}".format(err))
        # sys.exit(1)
    except configparser.ParsingError as err:
        print("Error: Slack configuration file parsing error. {0}".format(err))
        sys.exit(1)
    except:
        print("Error: Error in Slack configuration file.")
        sys.exit(1)
    
    return slack_config_dict


def post_message_to_slack(slack_config_dict, gcn_dict, json_dump):
    """
        Description:
            Post the received message to slack

        Args:
            slack_config_dict: slack configurations' dictionary
            gcn_dict: message's dictionary
            json_dump:
                True, if the message was received in json
                Flase, otherwise

        Returns:
            None

    """

    result = requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_config_dict['slack_token'],
        'channel': "#"+slack_config_dict['default_channel'],
        'text': prepare_message(gcn_dict) if json_dump else gcn_dict,
        'icon_url': slack_config_dict['slack_icon_url'],
        'username': slack_config_dict['slack_username'], }).json()

    print("Posting result: ", result)


def prepare_message(gcn_dict):
    """
        Description:
            Add pretty printing for message

        Args:
            gcn_dict : Received GCN message

        Returns:
            Formated GCN message for pretty printing
    """

    gcn_json = json.loads(json.dumps(gcn_dict))   
    gcn_header = gcn_json["header"]
    return ("*Title:* " + gcn_header['title'] + "\n" +
           "*Number:* " + str(gcn_header['number']) + "\n" +
           "*Subject:* " + gcn_header['subject'] + "\n" +
           "*Date*: " + str(gcn_header['date']) + "\n" +
           "*From:* " + gcn_header['from'] + "\n\n" + gcn_json['body'])

# ------------------------------------------------
# -- main


def _main(args=None):
    """
        Description:
            Parse and post GCN circulars to slack channel.

        Args:
            args: command-line args

        Returns:
            None
    """
    if not args:
        parser = argparse.ArgumentParser()
        _add_parser_args(parser)
        args = parser.parse_args()

    # load config if specified
    if args.config_file:
        config = args.config_file
    elif args.config:
        config = {opt[0]: opt[1] for opt in (kv.split("=") for kv in args.config)}
    else:
        config = None

    slack_config_dict = parse_slack_config_file(args.slack_config_file)

    # load consumer options

    # defaults:
    start_offset = 'latest'
    timeout = 10
    json_dump = False

    if args.json:
        json_dump = True
    if args.earliest:
        start_offset = 'earliest'
    if args.timeout:
        timeout = int(args.timeout)

    # read from topic

    # assume json format for the gcn
    gcn_format = 'json'

    with stream.open(args.broker_url, "r", format=gcn_format, config=config, start_at=start_offset) as s:
        # for _,gcn_dict in s(timeout=timeout):
        for _, gcn_dict in s:
            x = 1
            # post_message_to_slack(slack_config_dict, gcn_dict, json_dump)
