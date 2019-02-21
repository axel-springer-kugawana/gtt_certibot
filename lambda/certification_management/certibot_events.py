import json
import logging
import re
import requests
import urllib
from certification_management.business import Level
from certification_management.business import UserCertification
from certification_management.business import Voucher
from utils.configuration import Configuration


class CertibotEvents:
    def __init__(self, environment):
        # Logging configuration
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.environment = environment

    def launch(self, event):
        # Manage 'challenge' from Slack to validate the lambda.
        if "challenge" in event:
            return event["challenge"]

        slack_event = event['event']

        # Ignore message from bot.
        if not "bot_id" in slack_event \
           and slack_event['type'] == 'user_change' \
           and 'XfELFP2WL9' in slack_event['user']['profile']['fields']:

            # Application configuration
            config = Configuration(self.logger, self.environment)

            # Check input token
            if not event['token'] in config.slack_event_token:
                return "403 Forbidden"

            self.logger.info(slack_event['user']['real_name'] + " gets " + slack_event['user']['profile']['fields']['XfELFP2WL9']['value'] + " certification!")

            user_udid = slack_event['user']['id']
            user_level_name = re.search(' \((.+?) level\)', slack_event['user']['profile']['fields']['XfELFP2WL9']['value'].lower()).group(1)

            user = UserCertification.get(user_udid) # For now we force to use the first UserCertification - TODO manage multiple certification levels for one user
            level = Level.getByName(user_level_name)

            if user and level:
                user.passesCertification(level)

        return "200 OK"
