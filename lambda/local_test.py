import json
from lambda_handler import *

"""For test purpose"""
if __name__ == '__main__':
    event = '{"report":"True"}'
    handler(json.loads(event), None)
