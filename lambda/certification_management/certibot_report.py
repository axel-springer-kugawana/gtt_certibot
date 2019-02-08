import logging
import time
from certification_management.business import Certification
from certification_management.business import User
from certification_management.business import Voucher
from certification_management.business import Milestone
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

    def launch(self, reportType):
        start_time = time.time()
        certifications = Certification.getAll()
        vouchers = Voucher.getAll()
        milestones = Milestone.getAll()

        users = User.getAll()
        users_with_voucher = [user for user in users if user.voucher_code]
        users_with_profil = [user for user in users if user.profil_update_date]

        end_time = time.time()

        global_message = "*" + str(len(users)) + "* users in the challenge\n" \
            + "*" + str(len(users_with_voucher)) + "* already claimed a voucher code and " \
            + "*" + str(len(users_with_profil)) + "* have updated their profil"

        if len(milestones) > 0:
            global_message += "\n"
            for milestone in milestones:
                users_involved = [user for user in users_with_profil if user.profil_update_date <= milestone.date]

                stars_earned = 0
                for user in users_involved:
                    stars_earned += next((certification.stars for certification in certifications if certification.level == user.certification_level), None)

                users_involved_count = len(users_involved)
                global_message += "\n*Milestone #" + str(milestone.id) + "* for _" + milestone.date.strftime('%m/%d/%Y') + "_ - " + str(stars_earned) + "/" + str(milestone.goal) + " :star:"
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
            admin_message = "*" + str(len(certifications)) + "* certification levels\n" \
                + "*" + str(len(vouchers)) + "* voucher codes\n" \
                + global_message
            snippet = "\n".join([user.email for user in users_with_profil])

            if self.config.post_to_slack:
                self.kugawana_tool.post_notification_to_kugawana_slack(slack_channel=self.config.admin_slack_channel,
                                                                    title="Today's AWS certification report!",
                                                                    title_link="https://aws.amazon.com/fr/certification/",
                                                                    message=admin_message,
                                                                    level="good")
                if len(snippet) > 0:
                    self.kugawana_tool.post_snippet_to_kugawana_slack(slack_channel=self.config.admin_slack_channel,
                                                                    post_message=snippet)
            else:
                print(admin_message)
                print(snippet)
