import time
from slacker import Slacker


class KugawanaInventoryTool:
    def __init__(self, slack_token):
        self.slack = Slacker(slack_token)

    def post_notification_to_kugawana_slack(self, slack_channel, title, message, title_link=None, level=None, footer=None):
        """ This function helps you post a formatted message on a specific slack channel."""
        attachment = {
            "title": title,
            "title_link": title_link,
            "text": message,
            "color": level,
            "footer": footer,
        }
        self.slack.chat.post_message(channel=slack_channel, text="",
                                     as_user=True, attachments=[attachment])

    def post_snippet_to_kugawana_slack(self, slack_channel, post_message, initial_comment="", post_title=""):
        """ This function helps you post a snippet on a specific slack channel."""
        self.slack.files.upload(channels=slack_channel,
                                initial_comment=initial_comment,
                                title=post_title,
                                content=post_message)

    def post_object_integrity(self, inventory_function, build_object_string_function, tools_name, object_name, object_link, notification_slack_channel):
        """This method makes an inventory of generic objects.
        The result is posted in a snippet in a Slack channel."""

        title = " ".join([tools_name, object_name, "inventory"])
        title_link = object_link

        start_time = time.time()
        inventory = inventory_function()
        metrics = str(len(inventory)) + " " + object_name
        end_time = time.time()
        compute_time_information = "(compute time: " + \
            str(round(end_time - start_time, 3)) + ")"

        warnings = list()
        for object_inventory in inventory:
            if len(object_inventory.warning_reasons) > 0:
                warnings.append(object_inventory.format_string(
                    build_object_string_function))

        if len(warnings) > 0:
            level = "warning"  # "good", "warning", "danger" or hexa value for specific color
            message = metrics + "\n:warning: ALERT <!here|here>! There are " + \
                str(len(warnings)) + \
                " " + object_name + " with warnings. :warning:"
            snippet = "\n".join(warnings)

        else:
            level = "good"
            message = metrics

        self.post_notification_to_kugawana_slack(slack_channel=notification_slack_channel,
                                                 title=title,
                                                 title_link=title_link,
                                                 message=message,
                                                 level=level,
                                                 footer=compute_time_information)
        if len(warnings) > 0:
            self.post_snippet_to_kugawana_slack(slack_channel=notification_slack_channel,
                                                post_title="List of " + object_name + " with warnings",
                                                post_message=snippet)


class KugawanaAlert:
    def __init__(self, kugawana_object, reasons):
        self.kugawana_object = kugawana_object
        self.warning_reasons = reasons

    def format_string(self, build_str_function):
        return build_str_function(self.kugawana_object) + " (reasons: " + " - ".join(self.warning_reasons) + ")"
