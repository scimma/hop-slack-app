==========
Quickstart
==========

.. contents::
   :local:

The current status allows you to install Hop-on-Slack app in your own personal workspace. It is not released for distibution.

Prepare your Slack workspace
----------------------------

#. If you don't have a Slack workspace, create one `<https://slack.com/create#email>`_

#. Build your own Slack app `<https://api.slack.com/apps?new_app=1>`_ :

    #. Choose any name for the app.

    #. Choose your workspace where you want to install the app in.

    #. From the left-side menu, choose OAuth & Permissions.

    #. We need to give our application the permission to do actions in the workspace, i.e. send/read messages, create channels,...etc. Go to Scopes, choose chat:write (to send messages).
    
    #. Choose Install App to Workspace. Now in your workspace, you will find in your recent apps, your new app.
    
    #. Keep the bot token on the side for now.

Install application
-------------------
#. Clone the repo

.. code:: bash

    git clone `<https://github.com/scimma/hop-slack-app>`_

#. In the repo local directory, run:

.. code:: bash
    
    python setup.py install

#. Verify that hop-slack is installed:

.. code:: bash

    hop-slack --version

Run application
----------------

#. Prepare Slack configurations file. The file is organized into three sections:

    #. [SLACK_PROPERTIES] : It contains slack's token, username, icon_url,...
    #. [TOPIC_CHANNEL_MAPPING] : It contains the corresponding channels for the topics
    #. [GENERAL] : It contains general configurations, i.e create channel for topic if it does not exist.

    .. code-block:: text

        [SLACK_PROPERTIES]
        SLACK_TOKEN= xoxb-*****
        SLACK_USERNAME= Hop_SlackBot
        [TOPIC_CHANNEL_MAPPING]
        test= Testing
        gcn= GCN_Circular
        [GENERAL]
        DEFAULT_CHANNEL = general
        CREATE_CHANNEL = true

#. Run scimma-slack 

.. code:: bash

    scimma-slack subscribe -b <Broker_URL> -S <Slack_Config_File>

In case you have a server container running as:

.. code:: bash

    docker run -p 9092:9092 -v /tmp/kafka-logs:/tmp/kafka-logs -v /tmp/shared:/root/shared --hostname localhost scimma/server --noSecurity

You can have a slack command as

.. code:: bash

    scimma-slack subscribe -b kafka://localhost:9092/test -S /mnt/config_files/slack_config.cfg -e

Where:

* -b or --broker-url : Broker URL
* -e or --earliest : For posting the earliest received messages
* -S or --slack-config-File : Path to slack's configuration file
* -j or --json : Set the formate of the received message from broker
* -F or --config-file : Path to client'c configuration file
* -X or --config : Set client configuration via prop=val. Can be specified multiple times.
