# gtt_yabot

[![CircleCI](https://circleci.com/gh/axel-springer-kugawana/gtt_certibot.svg?style=svg&circle-token=9e33ae8a63586be2db59bf4aaeea2744b5ff385f)](https://circleci.com/gh/axel-springer-kugawana/gtt_certibot)

Certibot is a Slack bot allowing you to manage voucher code delivery.
It also includes an import script to initiate the database.

Trusted by our teams in Axel Springer, Certibot sends voucher codes to your teammates with zero friction.
You can import your vouchers and users details into its database with dedicated scripts.
Users will then have access to their personnal voucher codes at their fingertips.

## Prerequisites

To run the import module locally, you need to configure your AWSCLI. To do so, first install `awscli`:

```bash
pip install awscli
```

Then configure your `awscli` with your tokens:

```bash
aws configure
AWS Access Key ID [None]: <YOUR_AWS_ACCESS_KEY>
AWS Secret Access Key [None]: <YOUR_AWS_SECRET_ACCESS_KEY>
Default region name [None]: <YOUR_AWS_DEFAULT_REGION>
Default output format [None]: json
```

All python modules required are listed in [requirements.txt] file.

## Certibot - the slack bot

The bot works with slash commands:

* `/getvoucher`: allows a slack member to get his/her personnal voucher code. If a voucher code has already been sent to him/her, the command sends the same voucher again.

### Configuration

#### <a name="sensitivedatas"></a>Sensitive datas

To store sensitive data, we use AWS Secret manager. You will need to create a secret with the following structure:

```json
{
  "slack_event_token": <TOKEN_SEND_BY_SLACK_ON_BOT_EVENTS>,
  "admin_users": [
    <LIST_OF_ADMIN_SLACK_UDIDS>
  ]
}
```

Then specify in the [config.yml] file the secret name et the region you use.

#### Limited mode

You can disable interaction with the bot, for testing purposes, to all users except admins. In order to do so, change the `limited_mode` value to `True` in your [config.yml] file.
Once `limited_mode` has been enabled, only admins will be allowed to use slash commands. Admins can be listed in the AWS Secret manager (also check [Sensitive datas])

## Import module

Because you may have hundreds or thousands of users and personal voucher codes, we thought it might be helpful to enable developers to easily import csv files into the dynamoDB database that's behind all the magic of Certibot.
Simply upload your csv files into 'csv/to_transform/' and run python `python import_csv.py` in your favorite IDE.

You've got emails for your users and have no idea how to get their Slack UDID ? We've thought about it too and created a batch that transforms emails into UDIDs.
Simply upload your csv file into 'csv/to_transform/' and run `python transform_csv.py` in your favorite IDE

## Contributing

Please feel free to contact us for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Bruno MARQUET** - *initial work*
* **Romain BODY** - *initial work*

See also the list of [contributors] who participated in this project.

[requirements.txt]: requirements.txt
[config.yml]: lambda/config/config.yml
[sensitive datas]: #sensitivedatas
[contributors]: https://github.com/axel-springer-kugawana/gtt_yabot/contributors
