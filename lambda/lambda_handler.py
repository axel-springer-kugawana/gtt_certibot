import os
from yabot import Yabot

def handler(event, context):
    """This method is the start point for AWS lambda."""
    try:
        environment = os.environ['ENV']
    except KeyError:
        environment = "dev"

    yabot = Yabot(environment)
    yabot.launch(event)
