from utils.secret_managment import get_secret
import os
import hiyapyco

def getSlackToken():

    # Load configuration
    pkg_base = os.path.dirname(__file__)
    config_file = '{}/../config/config.yml'.format(pkg_base)
    config = hiyapyco.load(config_file, method=hiyapyco.METHOD_MERGE)

    # Load API token from AWS Secret Manager
    try:
        print("--- INFO: Load AWS secrets")
        api_tokens = get_secret()
        slack_token = api_tokens['slack_token']
        print("--- INFO: AWS secrets loaded with success")
    except:
        print("--- INFO: AWS secret failed, fallback with config file")
        slack_token = config['slack_token']
        print("--- INFO: Configuration file loaded with success")

    return slack_token