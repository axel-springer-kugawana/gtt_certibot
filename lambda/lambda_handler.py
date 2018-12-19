import os
from certification_management.yabot_certif import YabotCertif

def handler(event, context):
    """This method is the start point for AWS lambda."""
    try:
        environment = os.environ['ENV']
    except KeyError:
        environment = "dev"

    yabot_certif = YabotCertif(environment)
    yabot_certif.launch(event)
