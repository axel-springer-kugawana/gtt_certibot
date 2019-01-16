import os
import hiyapyco
from utils.secret_managment import get_secret


class Configuration:
    def __init__(self):

        # Load configuration
        pkg_base = os.path.dirname(__file__)
        config_file = ['{}/../config/config.yml'.format(pkg_base)]
        local_config_file = '{}/../config/local_config.yml'.format(pkg_base)
        if os.path.exists(local_config_file):
            config_file.append(local_config_file)
        config = hiyapyco.load(config_file, method=hiyapyco.METHOD_MERGE)

        aws_secret_name = config['aws_secret_name']
        aws_secret_region = config['aws_secret_region']

        # Load API token from AWS Secret Manager
        try:
            print("--- INFO: Load AWS secrets")
            secret = get_secret(aws_secret_name, aws_secret_region)
            self.slack_token = secret['slack_bot_token']
            print("--- INFO: AWS secrets loaded with success")
        except:
            print("--- INFO: AWS secret failed, fallback with config file")
            self.slack_token = config['slack_bot_token']
            print("--- INFO: Configuration file loaded with success")
