import datetime
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


class CertibotInteractiveMessages:
    def __init__(self, environment, token, user_id, callback_id, form, response_url):
        # Logging configuration
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # Application configuration
        self.config = Configuration(self.logger, environment)

        # Tools configuration
        self.sc = SlackClient(self.config.slack_app_token)

        # Interactive messages informations
        self.token = token
        self.user_id = user_id
        self.callback_id = callback_id
        self.form = form
        self.response_url = response_url

    def launch(self):
        response = ""

        # Check event
        if self.token == self.config.slack_event_token \
        and not(self.config.limited_mode and not self.user_id in self.config.admin_users):
            if self.callback_id == 'adduser':
                response = self.addUser(self.form['user_id'], int(self.form['certification_level']))
            if self.callback_id == 'addvouchers':
                response = self.addVouchers(self.form['voucher_codes'].split(','), self.form['availability_date'], int(self.form['certification_level']))
            else:
                response = {
                    "text": "Unknown callback_id (*" + self.callback_id + "*)"
                }
        else:
            response = {
                "text": "I'm under construction for now. Please be patient. ;)"
            }

        if response:
            headers = {
                "content-type": "application/json",
            }
            response = requests.request("POST", self.response_url, data=json.dumps(response), headers=headers)
            self.logger.info(response)

    def addUser(self, user_id, certification_level_id):
        response = ""

        user = User.get(user_id)
        levels = Level.getAll()
        certification_level = [level.name for level in levels if level.id == certification_level_id][0]

        if user:
            user_certification = [user_certification.level_id for user_certification in user.user_certifications if user_certification.level_id == certification_level_id]
            if user_certification:
                return {
                    "text": "<@" + self.form['user_id'] + "> already get a subscription for certification level *" + certification_level + "*"
                }

        # New user or existing user with a new certification level, so we add him/her
        if UserCertification(user_id, certification_level_id).add():
            response = {
                "text": "<@" + self.form['user_id'] + "> added with certification level *" + certification_level + "*"
            }
        else:
            response = {
                "text": "There is an error while adding <@" + self.form['user_id'] + ">"
            }

        return response

    def addVouchers(self, voucher_codes, availability_date, certification_level_id):
        response = ""

        success_list = list()
        error_list = list()
        for voucher_code in voucher_codes:
            try:
                if Voucher(voucher_code, certification_level_id, availability_date).add():
                    success_list.append(voucher_code)
                else:
                    error_list.append(voucher_code)
            except:
                error_list.append(voucher_code)

        message = str(len(success_list)) + " voucher codes added with success."
        if error_list and len(error_list) > 0:
            message += "\n" + str(len(error_list)) + " voucher codes not imported:\n" + '\n'.join(error_list)
        response = {
            "text": message
        }

        return response
