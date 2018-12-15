import logging
import urllib
from utils.configuration import Configuration


class Yabot:
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

            # Check input token
            if not data['token'] in config.allowed_input_tokens:
                return "403 Forbidden"

            if slack_event['channel_type'] == "im":
                # Someone call me on private message

                # Check if in limited mode (only a admin users are allowed to talk with Yabot)
                if config.limited_mode and not slack_event['user'] in config.admin_users:
                    reply = "Sorry, I'm not available for now. Please try again later. ;)"
                else:
                    reply = "ack im (" + slack_event['text'] + ")"

            else:
                if slack_event['channel_type'] in ['channel', 'group']:
                    # Someone call me on a channel

                    # Check if in limited mode (only a admin users are allowed to talk with Yabot)
                    if config.limited_mode and not slack_event['user'] in config.admin_users:
                        return "204 No Content"
                    else:
                        reply = "ack channel (" + slack_event['text'] + ")"
                else:
                    return "204 No Content"


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
