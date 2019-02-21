import boto3
import time

dynamodb = boto3.resource('dynamodb')
dynamodb.create_table(
    TableName='certibot_voucher',
        KeySchema=[
            {
                'AttributeName': 'code',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'code',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
)
