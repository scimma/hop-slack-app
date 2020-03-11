This is an application for SCiMMA on Slack where you can receive GCN messages

## Quickstart 

The current status allows you to install SCiMMA-on-Slack app in your own personal workspace. It is not released for distibution.

### Slack Workspace Preparation
 1. If you don't have a Slack workspace, create one https://slack.com/create#email
 2. Build your own Slack app: https://api.slack.com/apps?new_app=1
    1. Choose any name for the app
    2. Choose your workspace where you want to install the app in
    3. From the left-side menu, choose OAuth & Permissions
    4. We need to give our application the permission to do actions in the workspace, i.e. send/read messages, create channels,...etc. Go to Scopes, choose chat:write (to send messages). 
    5. Choose Install App to Workspace. Now in your workspace, you will find in your recent apps, your new app.
    6. Keep the bot token on the side for now.
    
### Application Preparation    
1. Clone the repo
```
git clone https://github.com/scimma/scimma-slack-app
```
2. In the repo local directory, run:
```
python3 setup.py install
```
Now, scimma-slack script is installed to /usr/local/python3.6/bin
try: scimma-slack --version, if it worked then you are good to go. Otherwise, you may need to create an alias for it for now or a symbolic link

3. Prepare Slack configurations file:
    The file is organized into three sections:
    1. [SLACK_PROPERTIES] : It contains slack's token, username, icon_url,...
    2. [TOPIC_CHANNEL_MAPPING] : It contains the corresponding channels for the topics
    3. [GENERAL] : It contains general configurations, i.e create channel for topic if it does not exist.
 A sample for the file:
    ``` 
    [SLACK_PROPERTIES]
    SLACK_TOKEN= xoxb-*****
    SLACK_USERNAME= SCiMMA_SlackBot
    [TOPIC_CHANNEL_MAPPING]
    test= Testing
    gcn= GCN_Circular
    [GENERAL]
    DEFAULT_CHANNEL = general
    CREATE_CHANNEL = true
    ```    
4. Run scimma-slack:
     ``` scimma-slack subscribe -b <Broker_URL> -S <Slack_Config_File> ```

In case you have a server container running as: 

```docker run -p 9092:9092 -v /tmp/kafka-logs:/tmp/kafka-logs -v /tmp/shared:/root/shared  --hostname localhost scimma/server --noSecurity```

You can have a slack command as

```scimma-slack subscribe -b kafka://localhost:9092/test -S /mnt/config_files/slack_config.cfg  -e```

Where:
* -b or --broker-url : Broker URL
* -e or --earliest : For posting the earliest received messages
* -S or --slack-config-File : Path to slack's configuration file
* -j or --json : Set the formate of the received message from broker
* -F or --config-file : Path to client'c configuration file
* -X or --config : Set client configuration via prop=val. Can be specified multiple times.
