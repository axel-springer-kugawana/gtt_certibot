import logging
import urllib
import certification_management
from fake_data import init_fake_data
from utils.configuration import Configuration


# For test purpose, to be moved to a real database
init_fake_data()


class YabotCertif:
    def __init__(self, environment):
        """ Logging configuration """
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.environment = environment

    def launch(self, data):
        # Manage 'challenge' from Slack to validate the lambda.
        if "challenge" in data:
            return data["challenge"]
        slack_event = data['event']

        # Ignore message from bot.
        if "bot_id" in slack_event:
            logging.warn("Ignore bot event")
        else:
            # Application configuration
            config = Configuration(self.logger, self.environment)

            # Check event
            if data['token'] in config.allowed_input_tokens \
            and slack_event['channel_type'] in ['im', 'channel', 'group'] \
            and not(config.limited_mode and not slack_event['user'] in config.admin_users):
                reply = ""

                if "yabot help" in slack_event['text']:
                    reply = "*Choose one of the following:* \
                    \n_list users_\
                    \n_list certifications_\
                    \n_list vouchers_\
                    \n_add certification <name> <level>_\
                    \n_add voucher <code> <level>_ \
                    \n_add user <email> <certification_level>_"
                else:
                    if "list certifications" in slack_event['text']:
                        reply += "*Certifications*\n" + "\n".join(str(certification) for certification in Certification.certifications)

                    if "list users" in slack_event['text']:
                        reply += "*Users*\n" + "\n".join(str(user) for user in User.users)

                    if "list vouchers" in slack_event['text']:
                        reply += "*Vouchers*\n" + "\n".join(str(voucher) for voucher in Voucher.vouchers)

                    if "add certification" in slack_event['text']:
                        certification_infos = slack_event['text'].split()
                        if not len(certification_infos) == 4:
                            reply = "Usage: add certification <name> <level> (whitespace is not permitted in name and level)"
                        else:
                            Certification(certification_infos[2], certification_infos[3]).add()
                            reply = "Certification added!"

                    if "add voucher" in slack_event['text']:
                        voucher_infos = slack_event['text'].split()
                        if not len(voucher_infos) == 4:
                            reply = "Usage: add voucher <code> <level> (whitespace is not permitted in code and level)"
                        else:
                            Voucher(voucher_infos[2], voucher_infos[3]).add()
                            reply = "Voucher added!"

                    if "add user" in slack_event['text']:
                        user_infos = slack_event['text'].split()
                        if not len(user_infos) == 4:
                            reply = "Usage: add user <email> <certification_level> (whitespace is not permitted in code and certification level)"
                        else:
                            User(user_infos[2], user_infos[3]).add()
                            reply = "User added!"

                channel_id = slack_event["channel"]
                data = urllib.parse.urlencode(
                    (
                        ("token", config.bot_token),
                        ("channel", channel_id),
                        ("text", reply)
                    )
                )
                data = data.encode("ascii")

                # Construct the HTTP request that will be sent to the Slack API.
                request = urllib.request.Request(
                    config.slack_url,
                    data=data,
                    method="POST"
                )
                # Add a header mentioning that the text is URL-encoded.
                request.add_header(
                    "Content-Type",
                    "application/x-www-form-urlencoded"
                )

                # Fire off the request!
                urllib.request.urlopen(request).read()

        # Everything went fine.
        return "200 OK"
