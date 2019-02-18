import unittest
from moto import mock_dynamodb2

import boto3
import time
from boto3.dynamodb.conditions import Key, Attr
from certification_management.business import Level
from certification_management.business import User
from certification_management.business import Voucher

class test_level(unittest.TestCase):
    mock_dynamodb = mock_dynamodb2()

    def setUp(self):
        self.mock_dynamodb.start()
        self.dynamodb = boto3.resource('dynamodb')
        self.dynamodb.create_table(
            TableName='awscert_level',
                KeySchema=[
                    {
                        'AttributeName': 'name',
                        'KeyType': 'HASH'
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'name',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
        )
        self.dynamodb.create_table(
            TableName='awscert_user',
                KeySchema=[
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
        )
        self.dynamodb.create_table(
            TableName='awscert_voucher',
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
        self.level_table = self.dynamodb.Table('awscert_level')
        self.user_table = self.dynamodb.Table('awscert_user')
        self.voucher_table = self.dynamodb.Table('awscert_voucher')

    def tearDown(self):
        self.mock_dynamodb.stop()

    def test_level_get(self):
        level_id = 'test_level_get_id'
        level_name = 'test_level_get_name'

        #given
        self.level_table.put_item(Item={'id': level_id, 'name': level_name})

        #when
        level = Level.get(level_id)

        #then
        assert level.id == level_id
        assert level.name == level_name

    def test_level_get_nonexistent(self):
        level_id = 'test_level_get_id'

        #given

        #when
        level = Level.get(level_id)

        #then
        assert level == None

    def test_level_add(self):
        level_id = 'test_level_add_id'
        level_name = 'test_level_add_name'
        level_stars = 1

        #given
        level = Level(level_id, level_name, level_stars)

        #when
        response = level.add()

        #then
        assert response == True
        certifs = self.level_table.query(KeyConditionExpression=Key('id').eq(level_id))['Items']
        assert len(certifs) == 1
        assert certifs[0]['id'] == level_id
        assert certifs[0]['name'] == level_name
        assert certifs[0]['stars'] == level_stars

    def test_level_remove(self):
        level_id = 'test_level_remove_id'
        level_name = 'test_level_remove_name'
        level_stars = 1

        #given
        self.level_table.put_item(Item={'id': level_id, 'name': level_name})
        level = Level(level_id, level_name, level_stars)

        #when
        response = level.remove()

        #then
        assert response == True
        certifs = self.level_table.query(KeyConditionExpression=Key('id').eq(level_id))['Items']
        assert len(certifs) == 0

    def test_level_remove_nonexistent(self):
        level_id = 'test_level_remove_id'
        level_name = 'test_level_remove_name'
        level_stars = 1

        #given
        level = Level(level_id, level_name, level_stars)

        #when
        response = level.remove()

        #then
        assert response == True
        certifs = self.level_table.query(KeyConditionExpression=Key('id').eq(level_id))['Items']
        assert len(certifs) == 0

    def test_level_remove_link_to_voucher(self):
        level_id = 'test_level_remove_id'
        level_name = 'test_level_remove_name'
        level_stars = 1
        voucher_code = 'test_level_remove_voucher_code'

        #given
        self.level_table.put_item(Item={'id': level_id, 'name': level_name})
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': level_id})
        level = Level(level_id, level_name, level_stars)

        #when
        response = level.remove()

        #then
        assert response == False
        certifs = self.level_table.query(KeyConditionExpression=Key('id').eq(level_id))['Items']
        assert len(certifs) == 1

    def test_level_remove_used_by_user(self):
        level_id = 'test_level_remove_id'
        level_name = 'test_level_remove_name'
        level_stars = 1
        user_id = 'test_level_remove_user_id'

        #given
        self.level_table.put_item(Item={'id': level_id, 'name': level_name})
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': level_id})
        level = Level(level_id, level_name, level_stars)

        #when
        response = level.remove()

        #then
        assert response == False
        certifs = self.level_table.query(KeyConditionExpression=Key('id').eq(level_id))['Items']
        assert len(certifs) == 1

    def test_level_str(self):
        level_name = 'test_level_str_name'
        certification_level = 'test_level_str_level'
        level_stars = 1

        #given
        level = Level(certification_level, level_name, level_stars)

        #when
        response = str(level)

        #then
        assert response != None


class test_user(unittest.TestCase):
    mock_dynamodb = mock_dynamodb2()

    def setUp(self):
        self.mock_dynamodb.start()
        self.dynamodb = boto3.resource('dynamodb')
        self.dynamodb.create_table(
            TableName='awscert_user',
                KeySchema=[
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
        )
        self.dynamodb.create_table(
            TableName='awscert_voucher',
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
        self.dynamodb.create_table(
            TableName='awscert_level',
                KeySchema=[
                    {
                        'AttributeName': 'name',
                        'KeyType': 'HASH'
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'name',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
        )
        self.user_table = self.dynamodb.Table('awscert_user')
        self.voucher_table = self.dynamodb.Table('awscert_voucher')
        self.level_table = self.dynamodb.Table('awscert_level')

    def tearDown(self):
        self.mock_dynamodb.stop()

    def test_user_get_without_voucher(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level})

        #when
        user = User.get(user_id)

        #then
        assert user.user_id == user_id
        assert user.certification_level == certification_level
        assert user.voucher_code == None

    def test_user_get_with_voucher(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'
        voucher_code = 'test_user_get_voucher_code'
        attribuated_date = 'test_user_get_attribuated_date'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level, 'voucher_code': voucher_code, 'attribuated_date': attribuated_date})

        #when
        user = User.get(user_id)

        #then
        assert user.user_id == user_id
        assert user.certification_level == certification_level
        assert user.voucher_code == voucher_code
        assert user.attribuated_date == attribuated_date

    def test_user_get_with_voucher_and_certification_passed(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'
        voucher_code = 'test_user_get_voucher_code'
        attribuated_date = 'test_user_get_attribuated_date'
        profile_update_date = 'test_user_get_profile_update_date'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level, 'voucher_code': voucher_code, 'attribuated_date': attribuated_date, 'profile_update_date': profile_update_date})

        #when
        user = User.get(user_id)

        #then
        assert user.user_id == user_id
        assert user.certification_level == certification_level
        assert user.voucher_code == voucher_code
        assert user.attribuated_date == attribuated_date
        assert user.profile_update_date == profile_update_date

    def test_user_get_nonexistent(self):
        user_id = 'test_user_get_id'

        #given

        #when
        user = User.get(user_id)

        #then
        assert user == None

    def test_user_add(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'

        #given
        user = User(user_id, certification_level)

        #when
        response = user.add()

        #then
        assert response == True
        users = self.user_table.scan(FilterExpression=Attr('user_id').eq(user_id))['Items']
        assert len(users) == 1
        assert users[0]['user_id'] == user_id
        assert users[0]['certification_level'] == certification_level

    def test_user_remove_without_voucher(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level})
        user = User(user_id, certification_level)

        #when
        response = user.remove()

        #then
        assert response == True
        users = self.user_table.scan(FilterExpression=Attr('user_id').eq(user_id))['Items']
        assert len(users) == 0

    def test_user_remove_with_voucher(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'
        voucher_code = 'test_user_get_voucher_code'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level, 'voucher_code': voucher_code})
        user = User(user_id, certification_level, voucher_code)

        #when
        response = user.remove()

        #then
        assert response == False
        users = self.user_table.scan(FilterExpression=Attr('user_id').eq(user_id))['Items']
        assert len(users) == 1

    def test_user_attribuateVoucher(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'
        voucher_code = 'test_user_get_voucher_code'
        voucher_availability = '01/01/2019'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level})
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level})
        user = User(user_id, certification_level)
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = user.attribuateVoucher(voucher)

        #then
        assert response == True
        assert user.voucher_code == voucher_code
        assert user.attribuated_date == time.strftime('%d/%m/%Y',time.localtime())

    def test_user_attribuateVoucher_already_attribuated(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'
        user_voucher_code = 'test_user_get_user_voucher_code'
        voucher_code = 'test_user_get_voucher_code'
        voucher_availability = '01/01/2019'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level, 'voucher_code': user_voucher_code})
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level})
        user = User(user_id, certification_level, user_voucher_code)
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = user.attribuateVoucher(voucher)

        #then
        assert response == False
        assert user.voucher_code == user_voucher_code

    def test_user_attribuateVoucher_wrong_level(self):
        user_id = 'test_user_get_id'
        certification_level = 'test_user_get_level'
        voucher_code = 'test_user_get_voucher_code'
        voucher_level = 'test_user_get_voucher_level'
        voucher_availability = '01/01/2019'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level})
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': voucher_level})
        user = User(user_id, certification_level)
        voucher = Voucher(voucher_code, voucher_level, voucher_availability)

        #when
        response = user.attribuateVoucher(voucher)

        #then
        assert response == False
        assert user.voucher_code == None

    def test_user_passesCertification(self):
        user_id = 'test_user_passes_id'
        level_id = 'test_level_passes_id'
        level_name = 'test_user_passes_level_name'
        level_stars = 1
        voucher_code = 'test_user_passes_voucher_code'

        #given
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': level_id, 'voucher_code': voucher_code})
        self.level_table.put_item(Item={'id': level_id, 'name': level_name})
        user = User(user_id, level_id, voucher_code)
        level = Level(level_id, level_name, level_stars)

        #when
        response = user.passesCertification(level)

        #then
        assert response == True
        assert user.profile_update_date == time.strftime('%d/%m/%Y',time.localtime())

    def test_user_passesCertification_already_saved(self):
        user_id = 'test_user_passes_id'
        level_name = 'test_user_passes_level_name'
        certification_level = 'test_user_passes_certification_level'
        level_stars = 1
        voucher_code = 'test_user_passes_voucher_code'
        attribuated_date = 'test_user_passes_attribuated_date'
        profile_update_date = 'test_user_passes_profile_update_date'

        #given
        user = User(user_id, certification_level, voucher_code, attribuated_date, profile_update_date)
        level = Level(certification_level, level_name, level_stars)

        #when
        response = user.passesCertification(level)

        #then
        assert response == False
        assert user.profile_update_date == profile_update_date

    def test_user_passesCertification_wrong_level(self):
        user_id = 'test_user_passes_id'
        user_level = 'test_user_passes_level'
        level_name = 'test_user_passes_level_name'
        certification_level = 'test_user_passes_certification_level'
        level_stars = 1
        voucher_code = 'test_user_passes_voucher_code'

        #given
        user = User(user_id, user_level, voucher_code)
        level = Level(certification_level, level_name, level_stars)

        #when
        response = user.passesCertification(level)

        #then
        assert response == False
        assert user.profile_update_date == None

    def test_user_passesCertification_without_voucher(self):
        user_id = 'test_user_passes_id'
        level_name = 'test_user_passes_level_name'
        certification_level = 'test_user_passes_certification_level'
        level_stars = 1

        #given
        user = User(user_id, certification_level)
        level = Level(certification_level, level_name, level_stars)

        #when
        response = user.passesCertification(level)

        #then
        assert response == False
        assert user.profile_update_date == None

    def test_user_str_without_voucher(self):
        user_id = 'test_user_str_id'
        certification_level = 'test_user_str_level'

        #given
        user = User(user_id, certification_level)

        #when
        response = str(user)

        #then
        assert response != None

    def test_user_str_with_voucher(self):
        user_id = 'test_user_str_id'
        certification_level = 'test_user_str_level'
        voucher_code = 'test_user_str_code'

        #given
        user = User(user_id, certification_level, voucher_code)

        #when
        response = str(user)

        #then
        assert response != None


class test_voucher(unittest.TestCase):
    mock_dynamodb = mock_dynamodb2()

    def setUp(self):
        self.mock_dynamodb.start()
        self.dynamodb = boto3.resource('dynamodb')
        self.dynamodb.create_table(
            TableName='awscert_user',
                KeySchema=[
                    {
                        'AttributeName': 'user_id',
                        'KeyType': 'HASH'
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'user_id',
                        'AttributeType': 'S'
                    },

                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
        )
        self.dynamodb.create_table(
            TableName='awscert_voucher',
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
        self.user_table = self.dynamodb.Table('awscert_user')
        self.voucher_table = self.dynamodb.Table('awscert_voucher')

    def tearDown(self):
        self.mock_dynamodb.stop()

    def test_voucher_get(self):
        voucher_code = 'test_voucher_get_code'
        voucher_availability = 'test_voucher_get_availability'
        certification_level = 'test_voucher_get_level'

        #given
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level, 'availability': voucher_availability})

        #when
        voucher = Voucher.get(voucher_code)

        #then
        assert voucher.code == voucher_code
        assert voucher.availability == voucher_availability
        assert voucher.certification_level == certification_level

    def test_voucher_get_nonexistent(self):
        voucher_code = 'test_voucher_get_code'

        #given

        #when
        voucher = Voucher.get(voucher_code)

        #then
        assert voucher == None

    def test_voucher_get_available_only_available(self):
        voucher_A_code = 'test_voucher_A_get_code'
        voucher_B_code = 'test_voucher_B_get_code'
        voucher_availability = 'test_voucher_get_availability'
        certification_level = 'test_voucher_get_level'

        #given
        self.voucher_table.put_item(Item={'code': voucher_A_code, 'certification_level': certification_level, 'availability': voucher_availability})
        self.voucher_table.put_item(Item={'code': voucher_B_code, 'certification_level': certification_level, 'availability': voucher_availability})

        #when
        voucher = Voucher.getAvailable(certification_level)

        #then
        assert voucher != None
        assert voucher.code in [voucher_A_code, voucher_B_code]

    def test_voucher_get_available_other_level(self):
        voucher_A_code = 'test_voucher_A_get_code'
        voucher_B_code = 'test_voucher_B_get_code'
        voucher_availability = 'test_voucher_get_availability'
        certification_level_A = 'test_voucher_get_level_A'
        certification_level_B = 'test_voucher_get_level_B'

        #given
        self.voucher_table.put_item(Item={'code': voucher_A_code, 'certification_level': certification_level_A, 'availability': voucher_availability})
        self.voucher_table.put_item(Item={'code': voucher_B_code, 'certification_level': certification_level_B, 'availability': voucher_availability})

        #when
        voucher = Voucher.getAvailable(certification_level_A)

        #then
        assert voucher != None
        assert voucher.code == voucher_A_code

    def test_voucher_get_available_unavailable(self):
        voucher_A_code = 'test_voucher_A_get_code'
        voucher_B_code = 'test_voucher_B_get_code'
        voucher_availability = 'test_voucher_get_availability'
        certification_level_A = 'test_voucher_get_level_A'
        certification_level_B = 'test_voucher_get_level_B'
        user_id = 'test_voucher_remove_user_id'
        attribuated_date = 'test_voucher_remove_attribuated_date'

        #given
        self.voucher_table.put_item(Item={'code': voucher_A_code, 'certification_level': certification_level_A, 'availability': voucher_availability})
        self.voucher_table.put_item(Item={'code': voucher_B_code, 'certification_level': certification_level_B, 'availability': voucher_availability})
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level_A, 'voucher_code': voucher_A_code, 'attribuated_date': attribuated_date})

        #when
        voucher = Voucher.getAvailable(certification_level_A)

        #then
        assert voucher == None

    def test_voucher_add(self):
        voucher_code = 'test_voucher_add_code'
        voucher_availability = 'test_voucher_add_availability'
        certification_level = 'test_voucher_add_level'

        #given
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = voucher.add()

        #then
        assert response == True
        vouchers = self.voucher_table.scan(FilterExpression=Attr('code').eq(voucher_code))['Items']
        assert len(vouchers) == 1
        assert vouchers[0]['code'] == voucher_code
        assert vouchers[0]['certification_level'] == certification_level
        assert vouchers[0]['availability'] == voucher_availability

    def test_voucher_remove_available(self):
        voucher_code = 'test_voucher_remove_code'
        voucher_availability = 'test_voucher_remove_availability'
        certification_level = 'test_voucher_remove_level'

        #given
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level, 'availability': voucher_availability})
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = voucher.remove()

        #then
        assert response == True
        vouchers = self.voucher_table.scan(FilterExpression=Attr('code').eq(voucher_code))['Items']
        assert len(vouchers) == 0

    def test_voucher_remove_unavailable(self):
        voucher_code = 'test_voucher_remove_code'
        voucher_availability = 'test_voucher_remove_availability'
        certification_level = 'test_voucher_remove_level'
        user_id = 'test_voucher_remove_user_id'
        attribuated_date = 'test_voucher_remove_attribuated_date'

        #given
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level, 'availability': voucher_availability})
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level, 'voucher_code': voucher_code, 'attribuated_date': attribuated_date})
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = voucher.remove()

        #then
        assert response == False
        vouchers = self.voucher_table.scan(FilterExpression=Attr('code').eq(voucher_code))['Items']
        assert len(vouchers) == 1

    def test_voucher_is_available(self):
        voucher_code = 'test_voucher_remove_code'
        voucher_availability = 'test_voucher_remove_availability'
        certification_level = 'test_voucher_remove_level'

        #given
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level, 'availability': voucher_availability})
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = voucher.isAvailable()

        #then
        assert response == True

    def test_voucher_is_unavailable(self):
        voucher_code = 'test_voucher_remove_code'
        voucher_availability = 'test_voucher_remove_availability'
        certification_level = 'test_voucher_remove_level'
        user_id = 'test_voucher_remove_user_id'
        attribuated_date = 'test_voucher_remove_attribuated_date'

        #given
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level, 'availability': voucher_availability})
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level, 'voucher_code': voucher_code, 'attribuated_date': attribuated_date})
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = voucher.isAvailable()

        #then
        assert response == False

    def test_voucher_str_available(self):
        voucher_code = 'test_voucher_str_available_id'
        voucher_availability = 'test_voucher_str_available_availability'
        certification_level = 'test_voucher_str_available_level'

        #given
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level, 'availability': voucher_availability})
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = str(voucher)

        #then
        assert response != None

    def test_voucher_str_unavailable(self):
        voucher_code = 'test_voucher_str_unavailable_id'
        voucher_availability = 'test_voucher_str_unavailable_availability'
        certification_level = 'test_voucher_str_unavailable_level'
        user_id = 'test_voucher_remove_user_id'
        attribuated_date = 'test_voucher_remove_attribuated_date'

        #given
        self.voucher_table.put_item(Item={'code': voucher_code, 'certification_level': certification_level, 'availability': voucher_availability})
        self.user_table.put_item(Item={'user_id': user_id, 'certification_level': certification_level, 'voucher_code': voucher_code, 'attribuated_date': attribuated_date})
        voucher = Voucher(voucher_code, certification_level, voucher_availability)

        #when
        response = str(voucher)

        #then
        assert response != None
