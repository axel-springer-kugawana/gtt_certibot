import os
from certification_management.certibot_commands import CertibotCommands
from certification_management.certibot_events import CertibotEvents

def handler(event, context):
    """This method is the start point for slash commands."""
    try:
        environment = os.environ['ENV']
    except KeyError:
        environment = "dev"

    token = event['token']
    user_id = event['user_id']
    command = event['command']
    try:
        text = event['text']
    except:
        text = ""   # Slash command has no text and is pretty straight forward
    response_url = event['response_url']

    certibot = CertibotCommands(environment, token, user_id, command, text, response_url)
    certibot.launch()

def event_handler(event, context):
    """This method is the start point for slack events."""
    try:
        environment = os.environ['ENV']
    except KeyError:
        environment = "dev"

    certibot = CertibotEvents(environment)
    return certibot.launch(event)
