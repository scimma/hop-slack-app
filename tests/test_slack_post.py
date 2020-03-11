#!/usr/bin/env python

import pytest
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

 
