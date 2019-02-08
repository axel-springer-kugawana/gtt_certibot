import json
from lambda_handler import *

"""For test purpose"""
if __name__ == '__main__':
    event = '{"report":"admin"}'
    handler(json.loads(event), None)
