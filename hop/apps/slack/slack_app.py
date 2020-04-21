#!/usr/bin/env python

__author__ = "Shereen Elsayed (s_elsayed@ucsb.edu)"
__description__ = "Post received messages to Slack channel"

import argparse
import configparser
import requests
import json
from genesis import streaming as stream


def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
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
        "-j",
        "--json", help="Request gcn output as raw json", action="store_true",
    )
    parser.add_argument(
        "-e",
        "--earliest",
        help="Request to stream from the earliest available Kafka offset",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help="Specifies the time (in seconds) to wait for new messages.",
    )

    # Slack configuration File
    parser.add_argument(
        "-S",
        "--slack-config-file",
        required=True,
        help="set Slack configuration from file ",
    )


def parse_slack_config_file(slack_config_file):
    """Parse slack configuration file

        Args:
            slack_config_file: Path to slack configuration file

        Returns:
            Dictionary with slack configurations
    """

    config = configparser.ConfigParser()
    slack_config_dict = {}
    try:
        config.read(slack_config_file)
        slack_config_dict = {
            "slack_token": config["SLACK_PROPERTIES"]["SLACK_TOKEN"],
            "slack_username": config["SLACK_PROPERTIES"]["SLACK_USERNAME"],
            "slack_icon_url": config["SLACK_PROPERTIES"]["SLACK_ICON_URL"],
            "topic_channel_mapping": {},
            "default_channel": config["GENERAL"]["DEFAULT_CHANNEL"],
        }
        slack_config_dict["topic_channel_mapping"] = config.items(
            "TOPIC_CHANNEL_MAPPING"
        )
        with open("config.txt", "w") as f:
            f.write(str(slack_config_dict))

    except IOError:
        raise IOError("Error: Slack configuration file does not appear to exist.")
    except configparser.NoSectionError:
        raise configparser.NoSectionError("Error: A section is missing")
    except configparser.DuplicateSectionError:
        raise configparser.DuplicateSectionError("Error: Section duplication error")
    except configparser.ParsingError:
        raise configparser.ParsingError("Error: Slack configuration file parsing error")
    except:
        raise Exception("Error: Error in Slack configuration file.")

    return slack_config_dict


def post_message_to_slack(slack_config_dict, gcn_dict, json_dump):
    """Post the received message to slack
        Args:
            slack_config_dict: slack configurations' dictionary
            gcn_dict: message's dictionary
            json_dump: True, if the message was received in json. Flase, otherwise
    """

    result = requests.post(
        "https://slack.com/api/chat.postMessage",
        {
            "token": slack_config_dict["slack_token"],
            "channel": "#" + slack_config_dict["default_channel"],
            "text": prepare_message(gcn_dict) if json_dump else gcn_dict,
            "icon_url": slack_config_dict["slack_icon_url"],
            "username": slack_config_dict["slack_username"],
        },
    ).json()

    print("Posting result: ", result)


def prepare_message(gcn_dict):
    """Add pretty printing for message

        Args:
            gcn_dict : Received GCN message

        Returns:
            Formated GCN message for pretty printing
    """
    gcn_json = json.loads(json.dumps(gcn_dict))
    return (
        "*Title:* {title}\n"
        "*Number:* {number}\n"
        "*Subject:* {subject}\n"
        "*Date*: {date}\n"
        "*From:* {from}\n\n"
        "{body}"
    ).format(**gcn_json["header"], body=gcn_json["body"])


# ------------------------------------------------
# -- main


def _main(args=None):
    """Parse and post GCN circulars to slack channel.

        Args:
            args: command-line args
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
    start_offset = "latest"
    timeout = 10
    json_dump = False

    if args.json:
        json_dump = True
    if args.earliest:
        start_offset = "earliest"
    if args.timeout:
        timeout = int(args.timeout)

    # read from topic

    # assume json format for the gcn
    gcn_format = "json"

    with stream.open(
        args.broker_url, "r", format=gcn_format, config=config, start_at=start_offset
    ) as s:
        for _, gcn_dict in s(timeout=timeout):
            post_message_to_slack(slack_config_dict, gcn_dict, json_dump)
