import logging
import time
from certification_management.business import Certification
from certification_management.business import User
from certification_management.business import Voucher
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

        """ Tools configuration """
        self.kugawana_tool = KugawanaInventoryTool(self.config.slack_bot_token)

    def launch(self):
        start_time = time.time()
        certifications = Certification.getAll()
        vouchers = Voucher.getAll()

        users = User.getAll()
        users_with_voucher = [user for user in users if user.voucher_code]
        users_with_profil = [user for user in users if user.profil_update_date]

        end_time = time.time()

        if self.config.post_to_slack:
            message = "*" + str(len(certifications)) + "* certification levels - " \
                + "*" + str(len(vouchers)) + "* vouchers\n" \
                + "*" + str(len(users)) + "* users in the challenge - " \
                + "*" + str(len(users_with_voucher)) + "* already claimed a voucher code - " \
                + "*" + str(len(users_with_profil)) + "* already update their profil"

            footer = "(compute time: " + \
                str(round(end_time - start_time, 3)) + ")"

            self.kugawana_tool.post_notification_to_kugawana_slack(slack_channel=self.config.slack_channel,
                                                                   title="Today's certification report!",
                                                                   title_link="https://aws.amazon.com/fr/certification/",
                                                                   message=message,
                                                                   footer=footer,
                                                                   level="good")

        else:
            print("Their are " + str(len(certifications)) + " certification levels.")
            print("Their are " + str(len(users)) + " users in the challenge.")
            print("Their are " + str(len(vouchers)) + " vouchers.")
