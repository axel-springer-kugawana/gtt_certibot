import os
from certification_management.yabot_certif import YabotCertif

def handler(event, context):
    """This method is the start point for AWS lambda."""
    try:
        environment = os.environ['ENV']
    except KeyError:
        environment = "dev"

    token = event['token']
    user_id = event['user_id']
    command = event['command']
    text = event['text']
    response_url = event['response_url']

    yabot_certif = YabotCertif(environment, token, user_id, command, text, response_url)
    yabot_certif.launch()
