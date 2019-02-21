import boto3
import time

dynamodb = boto3.resource('dynamodb')
dynamodb.create_table(
    TableName='certibot_certification',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
)
time.sleep(5) # Let AWS create the table
dynamodb.Table('certibot_certification').put_item(Item={'id': 1, 'name': 'AWS'})
dynamodb.Table('certibot_certification').put_item(Item={'id': 2, 'name': 'Salesforce'})
