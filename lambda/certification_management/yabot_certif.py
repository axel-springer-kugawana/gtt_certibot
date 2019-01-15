import json
import logging
import re
import requests
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
        self.config = Configuration(self.logger, self.environment)

        # Check event
        if self.token in self.config.allowed_input_tokens \
        and not(self.config.limited_mode and not self.user_id in self.config.admin_users):
            if self.command == '/getvoucher':
                return_text = self.getVoucher()

            elif self.command == '/getuservoucher':
                return_text = self.getUserVoucher()

            else:
                return_text = "Unknown command (" + self.command + ")"
        else:
            return_text = "I'm under construction for now. Please be patient. ;)"

        return return_text

    def getVoucher(self):
        user = User.get(self.user_id)
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

    def getUserVoucher(self):
        # Limited to admin users
        if not self.user_id in self.config.admin_users:
            return "Sorry this command is limited to administrators."

        # Check parameters
        if not self.parameter:
            return "Usage: /getuservoucher @user"

        # Get UDID from parameter (format: <@ABCD|username>)
        user_udid = ''
        user_name = ''
        try:
            user_udid = re.search('@(.+?)\|', self.parameter).group(1)
            user_name = re.search('\|(.+?)>', self.parameter).group(1)
        except AttributeError:
            user_udid = 'error'
            user_name = 'error'

        user = User.get(user_udid)
        if user:
            if user.voucher_code:
                voucher = Voucher.get(user.voucher_code)
                certification = Certification.get(voucher.certification_level)
                return "Hi! The personal voucher code for " + user_name + " for " + certification.name + \
                    " is: " + voucher.code + \
                    ". Please note that this voucher code is valid until " + voucher.availability + "."
            else:
                return user_name + " did not request his/her personnal voucher code yet."
        else:
            return "Hi! Unfortunately we couldn't find the user " + user_name + " in our data base."
