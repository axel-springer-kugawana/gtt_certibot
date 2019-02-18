import json
import logging
import re
import requests
import urllib
from certification_management.business import Level
from certification_management.business import User
from certification_management.business import Voucher
from utils.configuration import Configuration


class CertibotCommands:
    def __init__(self, environment, token, user_id, command, parameter, response_url):
        # Logging configuration
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # Application configuration
        self.config = Configuration(self.logger, environment)

        # Slash command informations
        self.token = token
        self.user_id = user_id
        self.command = command
        self.parameter = parameter
        self.response_url = response_url

    def launch(self):
        slash_response = ""

        # Check event
        if self.token == self.config.slack_event_token \
        and not(self.config.limited_mode and not self.user_id in self.config.admin_users):
            if self.command == '/getvoucher':
                slash_response = self.getVoucher()

            elif self.command == '/getuservoucher':
                slash_response = self.getUserVoucher()

            elif self.command == '/sendgift':
                slash_response = self.sendGift()

            else:
                slash_response = {
                    "text": "Unknown command (*" + self.command + "*)"
                }
        else:
            slash_response = {
                "text": "I'm under construction for now. Please be patient. ;)"
            }

        if not slash_response:
            slash_response = {
                "text": "Oops! Something went wrong, please try again." + \
                "If you are still facing trouble by the second time please contact <@UBRJ09SBE>."
            }

        headers = {
            "content-type": "application/json",
        }
        response = requests.request("POST", self.response_url, data=json.dumps(slash_response), headers=headers)
        self.logger.info(response)

    def getVoucher(self):
        payload = None
        user = User.get(self.user_id)
        if user:
            if user.voucher_code:
                voucher = Voucher.get(user.voucher_code)
                level = Level.get(voucher.certification_level)
                payload = {
                    "text": "Hi! Your personal voucher code for *" + level.name + \
                    "* level has been already requested by you: *" + voucher.code + \
                    "*. Please note that your voucher code is valid until *" + voucher.availability.strftime('%m/%d/%Y') + "*."
                }
            else:
                try:
                    voucher = Voucher.getAvailable(user.certification_level)
                    level = Level.get(voucher.certification_level)
                    if user.attribuateVoucher(voucher):
                        payload = {
                            "text": "Hi! Your personal voucher code for *" + level.name + \
                            "* level has been requested by you: *" + voucher.code + \
                            "*. Please note that your voucher code is valid until *" + voucher.availability.strftime('%m/%d/%Y') + "*."
                        }
                except Exception as e:
                    self.logger.warn(e)
                    payload = {
                        "text": "Hi! Unfortunately there are no more codes for *" + level.name + "* level available. " + \
                        "Please contact <@UBRJ09SBE> for more information and the ordering of new voucher codes."
                    }
        else:
            payload = {
                "text": "Hi! Unfortunately we couldn't find your personal voucher code in our data base. Please get back to <@UBRJ09SBE>."
            }

        return payload

    def getUserVoucher(self):
        payload = None

        # Limited to admin users
        if not self.user_id in self.config.admin_users:
            payload = {
                "text": "Sorry this command is limited to the bot administrators."
            }

        # Check parameters
        elif not self.parameter:
            payload = {
                "text": "Usage: /getuservoucher @user"
            }

        else:
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
                    level = Level.get(voucher.certification_level)

                    payload = {
                        "text": "Hi! The personal voucher code for *" + user_name + "* for *" + level.name + \
                        "* level is: *" + voucher.code + \
                        "*. Please note that this voucher code is valid until *" + voucher.availability.strftime('%m/%d/%Y') + "*."
                    }
                else:
                    payload = {
                        "text": "*" + user_name + "* did not request his/her personnal voucher code yet."
                    }
            else:
                payload = {
                    "text": "Hi! Unfortunately we couldn't find the user *" + user_name + "* in our data base."
                }

        return payload

    def sendGift(self):
        payload = None

        # Limited to admin users
        if not self.user_id in self.config.admin_users:
            payload = {
                "text": "Sorry this command is limited to the bot administrators."
            }

        # Check parameters
        elif not self.parameter:
            payload = {
                "text": "Usage: /sendgift @user"
            }

        else:
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
                if user.profile_update_date:
                    if user.sendGift():
                        payload = {
                            "text": "Hi! Thank you for sending a gift to *" + user_name + "*."
                        }
                else:
                    payload = {
                        "text": "*" + user_name + "* did not update his/her profile yet."
                    }
            else:
                payload = {
                    "text": "Hi! Unfortunately we couldn't find the user *" + user_name + "* in our data base."
                }

        return payload
