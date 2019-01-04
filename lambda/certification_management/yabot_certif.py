import requests
import json
import logging
import urllib
from certification_management.business import Certification
from certification_management.business import User
from certification_management.business import Voucher
from utils.configuration import Configuration


class YabotCertif:
    def __init__(self, environment, token, user_id, command, parameter, response_url):
        # Logging configuration
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        self.environment = environment
        self.token = token
        self.user_id = user_id
        self.command = command
        self.parameter = parameter
        self.response_url = response_url

    def launch(self):
        # Application configuration
        config = Configuration(self.logger, self.environment)

        # Check event
        if self.token in config.allowed_input_tokens \
        and not(config.limited_mode and not self.user_id in config.admin_users):
            if self.command == '/sendvoucher':
                return_text = self.sendVoucher()

            elif self.command == '/remindvoucher':
                return_text = self.remindVoucher()

            elif self.command == '/adduser':
                return_text = "Ok, user added! (placeholder)"

            else:
                return_text = "Unknown command (" + self.command + ")"
        else:
            return_text = "I'm under construction for now. Please be patient. ;)"

        response = requests.request("POST", self.response_url, data=return_text)
        print(response)

    def sendVoucher(self):
        user = User.get(self.parameter)
        if user:
            if user.voucher_code:
                voucher = Voucher.get(user.voucher_code)
                certification = Certification.get(voucher.certification_level)
                return "Hi! Your personal voucher code for " + certification.name + \
                    " has been already requested by you: " + voucher.code + \
                    ". Please note that your voucher code is valid until " + voucher.availability + "."
            else:
                try:
                    voucher = Voucher.getAvailable(user.certification_level)
                    certification = Certification.get(voucher.certification_level)
                    if user.attribuateVoucher(voucher):
                        return "Hi! Your personal voucher code for " + certification.name + \
                        " has been requested by you: " + voucher.code + \
                        ". Please note that your voucher code is valid until " + voucher.availability + "."
                    else:
                        return "Oops! Something went wrong. " + \
                        "Please make sure that you have entered the right email address and certification level and try again. " + \
                        "If you are still facing trouble by the second time please contact @Saskia KÖTTING."
                except:
                    return "Hi! Unfortunately there are no more codes for this certification level available. " + \
                    "Please contact @Saskia KÖTTING for more information and the ordering of new voucher codes."
        else:
            return "Hi! Unfortunately we couldn't find your personal voucher code in our data base. Please get back to @Saskia KÖTTING."

    def remindVoucher(self):
        user = User.get(self.parameter)
        if user:
            if user.voucher_code:
                voucher = Voucher.get(user.voucher_code)
                certification = Certification.get(voucher.certification_level)
                return "Hi! Your personal voucher code for " + certification.name + \
                    " is: " + voucher.code + \
                    ". Please note that your voucher code is valid until " + voucher.availability + "."
            else:
                return "You did not request your personnal voucher code yet. Please use /sendvoucher command."
        else:
            return "Hi! Unfortunately we couldn't find your personal voucher code in our data base. Please get back to @Saskia KÖTTING."
