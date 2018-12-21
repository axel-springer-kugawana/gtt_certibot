import requests
import json
import logging
import urllib
from certification_management.business import Certification
from certification_management.business import User
from certification_management.business import Voucher
from utils.configuration import Configuration


class YabotCertif:
    def __init__(self, environment):
        # Logging configuration
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.environment = environment

    def launch(self, event):
        # Application configuration
        config = Configuration(self.logger, self.environment)

        # Check event
        if event['token'] in config.allowed_input_tokens \
        and not(config.limited_mode and not event['user_id'] in config.admin_users):
            if event['command'] == '/sendvoucher':
                email = event['text']
                user = User.get(email)
                if user:
                    if user.voucher_code:
                        voucher = Voucher.get(user.voucher_code)
                        return_text = "Hi! Your personal voucher code for " + voucher.certification_level + \
                            " has been already requested by you: " + voucher.code + \
                            ". Please note that your voucher code is valid until " + voucher.availability + "."
                    else:
                        voucher = Voucher.getAvailable(user.certification_level)
                        if voucher:
                            if user.attribuateVoucher(voucher):
                                return_text = "Hi! Your personal voucher code for " + voucher.certification_level + \
                                " has been requested by you: " + voucher.code + \
                                ". Please note that your voucher code is valid until " + voucher.availability + "."
                            else:
                                return_text = "Oops! Something went wrong. " + \
                                "Please make sure that you have entered the right email address and certification level and try again. " + \
                                "If you are still facing trouble by the second time please contact @Saskia KÖTTING."
                        else:
                            return_text = "Hi! Unfortunately there are no more codes for this certification level available. " + \
                            "Please contact @Saskia KÖTTING for more information and the ordering of new voucher codes."
                else:
                    return_text = "Hi! Unfortunately we couldn't find your personal voucher code in our data base. Please get back to @Saskia KÖTTING."

            elif event['command'] == '/adduser':
                return_text = "Ok, user added! (placeholder)"

            else:
                return_text = "Unknown command (" + event['command'] + ")"

            payload = {
                'text': return_text,
                'attachments': [{}]
            }
            headers = {
                'content-type': "application/json",
            }

            response = requests.request("POST", event['response_url'], data=json.dumps(payload), headers=headers)
            print(response)
