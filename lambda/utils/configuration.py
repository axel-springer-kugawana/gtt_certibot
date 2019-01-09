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
        local_config_file = '{}/../config/local_config.yml'.format(pkg_base)
        if os.path.exists(config_file_env):
            config_file.append(config_file_env)
        if os.path.exists(local_config_file):
            config_file.append(local_config_file)
        config = hiyapyco.load(config_file, method=hiyapyco.METHOD_MERGE)

        self.limited_mode = config['limited_mode']

        # Load sensitives data from AWS Secret Manager
        try:
            logger.info("Load AWS secret")
            secret = get_secret()
            self.bot_token = secret['bot_token']
            self.allowed_input_tokens = secret['allowed_input_tokens']
            self.admin_users = secret['admin_users']
            logger.info("AWS secret loaded with success")
        except:
            logger.info("AWS secret failed, fallback with config file")
            self.bot_token = config['bot_token']
            self.allowed_input_tokens = config['allowed_input_tokens']
            self.admin_users = config['admin_users']
            logger.info("Configuration file loaded with success")
