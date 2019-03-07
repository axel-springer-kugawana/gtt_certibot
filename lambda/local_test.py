import json
from lambda_handler import *

"""For test purpose"""
if __name__ == '__main__':
    event = '{"report":"admin"}'
    #event = '{"token":"tbd", "user_id":"user_id", "command": "/getvoucher", "response_url": "response_url"}'
    #event = '{"token":"tbd", "user_id":"user_id", "command": "/sendgift", "text": "<@user_id|user_name>", "response_url": "response_url"}'
    handler(json.loads(event), None)
