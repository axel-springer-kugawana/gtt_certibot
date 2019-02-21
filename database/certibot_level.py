import boto3
import time

dynamodb = boto3.resource('dynamodb')
dynamodb.create_table(
    TableName='certibot_level',
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
dynamodb.Table('certibot_level').put_item(Item={'id': 1, 'name': 'foundational', 'certification_id': 1, 'stars': 1})
dynamodb.Table('certibot_level').put_item(Item={'id': 2, 'name': 'professionnal', 'certification_id': 1, 'stars': 3})
dynamodb.Table('certibot_level').put_item(Item={'id': 3, 'name': 'associate', 'certification_id': 1, 'stars': 2})
dynamodb.Table('certibot_level').put_item(Item={'id': 4, 'name': 'specialty', 'certification_id': 1, 'stars': 3})

