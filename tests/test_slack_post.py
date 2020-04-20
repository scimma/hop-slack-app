#!/usr/bin/env python

import pytest
from unittest.mock import patch
import configparser
from hop.apps.slack import slack_app
from hop.apps.slack import __version__


@pytest.mark.script_launch_mode("subprocess")
def test_help_version(script_runner):
    ret = script_runner.run("hop-slack", "--help")
    assert ret.success

    ret = script_runner.run("hop-slack", "--version")
    assert ret.success

    assert ret.stdout == f"hop-slack version {__version__}\n"
    assert ret.stderr == ""


def test_message_preparation_for_slack(shared_datadir):

    test_content = (
        shared_datadir / "test_data" / "26936_gcn_circular_dict.json"
    ).read_text()
    with patch("hop.apps.slack.slack_app.json.dumps") as mock_load:
        mock_load.return_value = test_content
        test_result = slack_app.prepare_message(test_content)
        with open("file2.txt", "w") as f:
            f.write(test_result)
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
    with open("file.txt", "w") as f:
        f.write(str(test_result))
    assert (
        str(test_result)
        == (shared_datadir / "expected_data" / "parsed_slack_config.txt").read_text()
    )

    # Corrupted configuration file: duplicated section
    config_file_path = str(
        shared_datadir / "test_data" / "slack_config_dup_section.cfg"
    )

    with pytest.raises(configparser.DuplicateSectionError):
        test_result = slack_app.parse_slack_config_file(str(config_file_path))
