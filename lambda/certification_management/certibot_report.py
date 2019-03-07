import logging
import re
import time
from certification_management.business import Level
from certification_management.business import UserCertification
from certification_management.business import Voucher
from certification_management.business import Milestone
from slackclient import SlackClient
from utils.configuration import Configuration
from utils.kugawana_inventory_tools import KugawanaInventoryTool

class CertibotReport:
    def __init__(self, environment):
        # Logging configuration
        logging.basicConfig()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # Application configuration
        self.config = Configuration(self.logger, environment)

        # Tools configuration
        self.kugawana_tool = KugawanaInventoryTool(self.config.slack_bot_token)
        self.sc = SlackClient(self.config.slack_app_token)

    def launch(self, reportType):
        start_time = time.time()
        levels = Level.getAll()
        vouchers = Voucher.getAll()
        milestones = Milestone.getAll()

        users = UserCertification.getAll()
        users_with_voucher = [user for user in users if user.voucher_code]
        users_with_profile = [user for user in users if user.profile_update_date]
        users_without_gift = [user for user in users_with_profile if not user.gift_sent_date]

        end_time = time.time()

        global_message = "*" + str(len(users)) + "* users in the challenge\n" \
            + "*" + str(len(users_with_voucher)) + "* already claimed a voucher code and " \
            + "*" + str(len(users_with_profile)) + "* have updated their profile"

        if len(milestones) > 0:
            global_message += "\n"
            for milestone in milestones:
                users_involved = [user for user in users_with_profile if user.profile_update_date <= milestone.date]

                stars_earned = 0
                for user in users_involved:
                    stars_earned += next((level.stars for level in levels if level.id == user.level_id), None)

                users_involved_count = len(users_involved)
                global_message += "\n*Milestone #" + str(milestone.id) + "* for _" + milestone.date.strftime('%d/%m/%Y') + "_ - " + str(stars_earned) + "/" + str(milestone.goal) + " :star:"
                if stars_earned > 0:
                    global_message += " _(" + str(users_involved_count) + " people involved)_"

        if reportType == 'user':
            # Users report
            user_message = global_message \
                + "\nDon't know how to get your certification? Go to https://kugawana.atlassian.net/wiki/x/DYAkAg"

            footer = "(compute time: " + \
                str(round(end_time - start_time, 3)) + ")"

            if self.config.post_to_slack:
                self.kugawana_tool.post_notification_to_kugawana_slack(slack_channel=self.config.slack_channel,
                                                                    title="Latest AWS certification report!",
                                                                    title_link="https://aws.amazon.com/fr/certification/",
                                                                    message=user_message,
                                                                    footer=footer,
                                                                    level="good")
            else:
                print(user_message)
                print(footer)

        elif reportType == 'admin':
            # Admin report
            admin_message = "*" + str(len(levels)) + "* certification levels\n" \
                + "*" + str(len(vouchers)) + "* voucher codes\n" \
                + global_message
            users_details = "\n".join(["<@" + user.user_id + ">" for user in users_without_gift])

            # Check profile synch of all users with voucher code
            users_out_of_sync = list()
            users_profile_voucher_not_matched = list()
            for user in users_with_voucher:
                if not user.profile_update_date:
                    try:
                        profile = self.sc.api_call(method="users.profile.get", user=user.user_id)['profile']['fields']['XfELFP2WL9']['value']
                        if profile:
                            user_level_name = re.search(' \((.+?) level\)', profile.lower()).group(1)
                            certification_level = [level for level in levels if level.name == user_level_name][0]
                            if user.level_id == certification_level:
                                users_out_of_sync.append(user)
                            else:
                                users_profile_voucher_not_matched.append(user)
                    except Exception as e:
                        self.logger.warn(e)

            users_out_of_sync_report = "\n".join(["<@" + user.user_id + ">" for user in users_out_of_sync])
            users_profile_voucher_not_matched_report = "\n".join(["<@" + user.user_id + ">" for user in users_profile_voucher_not_matched])

            footer = "(compute time: " + \
                str(round(end_time - start_time, 3)) + ")"

            if self.config.post_to_slack:
                self.kugawana_tool.post_notification_to_kugawana_slack(slack_channel=self.config.admin_slack_channel,
                                                                    title="Today's AWS certification report!",
                                                                    title_link="https://aws.amazon.com/fr/certification/",
                                                                    message=admin_message,
                                                                    footer=footer,
                                                                    level="good")
                if len(users_details) > 0:
                    self.kugawana_tool.post_notification_to_kugawana_slack(slack_channel=self.config.admin_slack_channel,
                                                                        title="List of users who did not receive their gift",
                                                                        message=users_details,
                                                                        level="0576b9")
                if len(users_out_of_sync_report) > 0:
                    self.kugawana_tool.post_notification_to_kugawana_slack(slack_channel=self.config.admin_slack_channel,
                                                                           title="List of users with their profile out of sync",
                                                                           message=users_out_of_sync_report,
                                                                           level="danger")
                if len(users_profile_voucher_not_matched_report) > 0:
                    self.kugawana_tool.post_notification_to_kugawana_slack(slack_channel=self.config.admin_slack_channel,
                                                                           title="List of users with their profile not matching their voucher level",
                                                                           message=users_profile_voucher_not_matched_report,
                                                                           level="warning")
            else:
                print(admin_message)
                print(users_details)
                print(users_out_of_sync_report)
                print(users_profile_voucher_not_matched_report)
