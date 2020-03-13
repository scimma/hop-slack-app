#!/usr/bin/env python

import pytest
import json
import re
from unittest.mock import patch
from scimma.apps.slack import slack_app
from scimma.apps.slack import __version__


@pytest.mark.script_launch_mode("subprocess")
def test_help_version(script_runner):
    ret = script_runner.run("scimma-slack", "--help")
    assert ret.success

    ret = script_runner.run("scimma-slack", "--version")
    assert ret.success

    assert ret.stdout == f"scimma-slack version {__version__}\n"
    assert ret.stderr == ""


def test_message_preparation_for_slack(shared_datadir):

    test_content = (
        shared_datadir / "test_data" / "26936_gcn_circular_dict.json"
    ).read_text()
    with patch("scimma.apps.slack.slack_app.json.dumps") as mock_load:
        mock_load.return_value = test_content
        test_result = slack_app.prepare_message(test_content)
        assert (
            test_result
            == (
                shared_datadir / "expected_data" / "26936_gcn_circular_PP.txt"
            ).read_text()
        )



def test_parse_slack_config(shared_datadir, capsys):

    # Normal configuration file
    config_file_path = str(shared_datadir / "test_data" / "slack_configuration.cfg")
    test_result = slack_app.parse_slack_config_file(str(config_file_path))
    assert (
        json.dumps(test_result)
        == (shared_datadir / "expected_data" / "parsed_slack_config.txt").read_text()
    )

    # Corrupted configuration file: duplicated section
    config_file_path = str(
        shared_datadir / "test_data" / "slack_config_dup_section.cfg"
    )
    test_result = slack_app.parse_slack_config_file(str(config_file_path))
    captured = capsys.readouterr()
    error_msg = captured.out

    # replace the path in the captured error with empty string
    pattern = re.compile(r"(\/.*?\.[\w:]+)")
    match = pattern.findall(error_msg)
    assert len(match) > 0
    result = error_msg.replace(match[0], "", 1)
    assert (
        result
        == "Error: Section duplication error. While reading from '' [line 15]: section 'GENERAL' already exists\n"
    )