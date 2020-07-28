#!/usr/bin/env python

__author__ = "Shereen Elsayed (s_elsayed@ucsb.edu)"
__description__ = "Post received messages to Slack channel"

import argparse
import configparser
import requests
import json

from hop import Stream
from hop import cli
from hop import io


def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """

    cli.add_client_opts(parser)

    # Subscription option
    parser.add_argument(
        "-s",
        "--start-at",
        choices=io.StartPosition.__members__,
        default=str(io.StartPosition.LATEST).upper(),
        help="Set the message offset offset to start at. Default: LATEST.",
    )
    parser.add_argument(
        "-p",
        "--persist",
        action="store_true",
        help="If set, persist or listen to messages indefinitely. "
             "Otherwise, will stop listening when EOS is received.",
    )
    parser.add_argument(
        "-j", "--json", help="Request message output as raw json", action="store_true",
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


def post_message_to_slack(slack_config_dict, gcn, json_dump):
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
            "text": prepare_message(gcn) if json_dump else str(gcn),
            "icon_url": slack_config_dict["slack_icon_url"],
            "username": slack_config_dict["slack_username"],
        },
    ).json()

    print("Posting result: ", result)


def prepare_message(gcn):
    """Add pretty printing for message

        Args:
            gcn : Received GCN message

        Returns:
            Formated GCN message for pretty printing
    """
    gcn_dict = gcn.asdict()
    return (
        "*Title:* {title}\n"
        "*Number:* {number}\n"
        "*Subject:* {subject}\n"
        "*Date*: {date}\n"
        "*From:* {from}\n\n"
        "{body}"
    ).format(**gcn_dict["header"], body=gcn_dict["body"])


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

    slack_config_dict = parse_slack_config_file(args.slack_config_file)

    # read from topic
    start_at = io.StartPosition[args.start_at]
    stream = io.Stream(auth=(not args.no_auth), start_at=start_at, persist=args.persist)

    with stream.open(args.url, "r") as s:
        for circular in s:
            post_message_to_slack(slack_config_dict, circular, args.json)
