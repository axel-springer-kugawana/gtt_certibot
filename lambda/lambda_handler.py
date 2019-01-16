import os
from certification_management.certibot import Certibot

def handler(event, context):
    """This method is the start point for AWS lambda."""
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

    certibot = Certibot(environment, token, user_id, command, text, response_url)
    certibot.launch()
