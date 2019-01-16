import os
import hiyapyco
from utils.secret_managment import get_secret


class Configuration:
    def __init__(self, logger, environment):

        # Load configuration
        pkg_base = os.path.dirname(__file__)
        config_file = ['{}/../config/config.yml'.format(pkg_base)]
        config_file_env = '{}/../config/{}/config.yml'.format(
            pkg_base, environment)
        if os.path.exists(config_file_env):
            config_file.append(config_file_env)
        local_config_file = '{}/../config/local_config.yml'.format(pkg_base)
        if os.path.exists(local_config_file):
            config_file.append(local_config_file)
        config = hiyapyco.load(config_file, method=hiyapyco.METHOD_MERGE)

        self.limited_mode = config['limited_mode']
        aws_secret_name = config['aws_secret_name']
        aws_secret_region = config['aws_secret_region']

        # Load sensitives data from AWS Secret Manager
        try:
            logger.info("Load AWS secret")
            secret = get_secret(aws_secret_name, aws_secret_region)
            self.slack_event_token = secret['slack_event_token']
            self.admin_users = secret['admin_users']
            logger.info("AWS secret loaded with success")
        except:
            logger.info("AWS secret failed, fallback with config file")
            self.slack_event_token = config['slack_event_token']
            self.admin_users = config['admin_users']
            logger.info("Configuration file loaded with success")
