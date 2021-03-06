import json
import logging
import re
import requests
import urllib
from certification_management.business import Level
from certification_management.business import User
from certification_management.business import UserCertification
from certification_management.business import Voucher
from slackclient import SlackClient
from utils.configuration import Configuration


class CertibotCommands:
    def __init__(self, environment, token, user_id, command, parameter, response_url, trigger_id):
        # Logging configuration
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # Application configuration
        self.config = Configuration(self.logger, environment)

        # Tools configuration
        self.sc = SlackClient(self.config.slack_app_token)

        # Slash command informations
        self.token = token
        self.user_id = user_id
        self.command = command
        self.parameter = parameter
        self.response_url = response_url
        self.trigger_id = trigger_id

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

            elif self.command == '/adduser':
                self.addUser()

            elif self.command == '/addvouchers':
                self.addVouchers()

            else:
                slash_response = {
                    "text": "Unknown command (*" + self.command + "*)"
                }
        else:
            slash_response = {
                "text": "I'm under construction for now. Please be patient. ;)"
            }

        if slash_response:
            headers = {
                "content-type": "application/json",
            }
            response = requests.request("POST", self.response_url, data=json.dumps(slash_response), headers=headers)
            self.logger.info(response)

    def getVoucher(self):
        payload = None
        user = User.get(self.user_id)
        if user:
            for user_certification in user.user_certifications:
                if not user_certification.voucher_code:
                    try:
                        voucher = Voucher.getAvailable(int(user_certification.level_id))
                        user_certification.attribuateVoucher(voucher)
                    except Exception as e:
                        self.logger.warn(e)

            payload = {
                "blocks": [
                    {
                        "type": "section",
                        "block_id": "section001",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Hi! Here are your personal voucher codes"
                        }
                    },
                    {
                        "type": "section",
                        "block_id": "section002",
                        "fields": user.formatSlackFields()
                    }
                ]
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
                payload = {
                    "blocks": [
                        {
                            "type": "section",
                            "block_id": "section001",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Hi! Here are personal voucher codes for <@" + user_udid + ">"
                            }
                        },
                        {
                            "type": "section",
                            "block_id": "section002",
                            "fields": user.formatSlackFields()
                        }
                    ]
                }
            else:
                payload = {
                    "text": "Hi! Unfortunately we couldn't find the user <@" + user_udid + "> in our data base."
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

            user = UserCertification.get(user_udid)
            if user:
                user = user[0] # For now we force to use the first UserCertification - TODO manage multiple certification levels for one user
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

    def addUser(self):
        # Limited to admin users
        if not self.user_id in self.config.admin_users:
            payload = {
                "text": "Sorry this command is limited to the bot administrators."
            }

        else:
            dialog = {
                "callback_id": "adduser",
                "title": "Add a Certibot user",
                "submit_label": "Add",
                "elements": [
                    {
                        "label": "Choose a user",
                        "type": "select",
                        "data_source": "users",
                        "name": "user_id"
                    },
                    {
                        "label": "Choose a certification level",
                        "name": "certification_level",
                        "type": "select",
                        "option_groups": [
                            {
                                "label": "AWS",
                                "options": [
                                    {
                                        "label": "Foundational",
                                        "value": 1
                                    },
                                    {
                                        "label": "Associate",
                                        "value": 3
                                    },
                                    {
                                        "label": "Professionnal",
                                        "value": 2
                                    },
                                    {
                                        "label": "Speciaity",
                                        "value": 4
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            self.sc.api_call(method="dialog.open", trigger_id=self.trigger_id, dialog=dialog)

    def addVouchers(self):
        # Limited to admin users
        if not self.user_id in self.config.admin_users:
            payload = {
                "text": "Sorry this command is limited to the bot administrators."
            }

        else:
            dialog = {
                "callback_id": "addvouchers",
                "title": "Add a Certibot voucher",
                "submit_label": "Add",
                "elements": [
                    {
                        "label": "Voucher codes",
                        "type": "textarea",
                        "name": "voucher_codes",
                        "hint": "Provide list of voucher codes separated by comma (,)."
                    },
                    {
                        "label": "Availability date",
                        "name": "availability_date",
                        "type": "text",
                        "placeholder": "DD/MM/YYYY"
                    },
                    {
                        "label": "Choose a certification level",
                        "name": "certification_level",
                        "type": "select",
                        "option_groups": [
                            {
                                "label": "AWS",
                                "options": [
                                    {
                                        "label": "Foundational",
                                        "value": 1
                                    },
                                    {
                                        "label": "Associate",
                                        "value": 3
                                    },
                                    {
                                        "label": "Professionnal",
                                        "value": 2
                                    },
                                    {
                                        "label": "Speciaity",
                                        "value": 4
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            self.sc.api_call(method="dialog.open", trigger_id=self.trigger_id, dialog=dialog)
