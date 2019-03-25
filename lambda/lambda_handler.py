import os
from certification_management.certibot_commands import CertibotCommands
from certification_management.certibot_events import CertibotEvents
from certification_management.certibot_interactive_messages import CertibotInteractiveMessages
from certification_management.certibot_report import CertibotReport

def handler(event, context):
    try:
        environment = os.environ['ENV']
    except KeyError:
        environment = "dev"

    if 'event' in event:
        # This is a Slack event
        certibot = CertibotEvents(environment)
        return certibot.launch(event)

    elif 'type' in event and event['type'] == "dialog_submission":
        # This is an interactive message
        token = event['token']
        user_id = event['user']['id']
        callback_id = event['callback_id']
        form = event['submission']
        response_url = event['response_url']

        certibot = CertibotInteractiveMessages(environment, token, user_id, callback_id, form, response_url)
        certibot.launch()

    elif 'token' in event:
        # This is a Slack slash command
        token = event['token']
        user_id = event['user_id']
        command = event['command']
        response_url = event['response_url']

        try:
            text = event['text']
        except:
            text = ""   # Slash command has no text and is pretty straight forward

        try:
            trigger_id = event['trigger_id']
        except:
            trigger_id = ""

        certibot = CertibotCommands(environment, token, user_id, command, text, response_url, trigger_id)
        certibot.launch()

    elif 'report' in event:
        # This is a Cloudwatch triggered call
        certibot = CertibotReport(environment)
        certibot.launch(event['report'])

