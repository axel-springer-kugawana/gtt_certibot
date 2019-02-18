import boto3
import datetime
import time
from boto3.dynamodb.conditions import Key, Attr


class Level:
    levels = boto3.resource('dynamodb').Table('awscert_level')

    def __init__(self, id, name, stars):
        self.id = id
        self.name = name
        self.stars = stars

    def __str__(self):
        return "Id: " + self.id + ", name: " + self.name + ", stars: " + self.stars

    def add(self):
        Level.levels.put_item(Item={'id': self.id, 'name': self.name, 'stars': self.stars})
        return True

    def remove(self):
        if len(Voucher.vouchers.scan(FilterExpression=Attr('certification_level').eq(self.id))['Items']) == 0 \
           and len(User.users.scan(FilterExpression=Attr('certification_level').eq(self.id))['Items']) == 0:
            Level.levels.delete_item(Key={'id': self.id})
            return True
        return False

    @classmethod
    def __map(cls, dbitem):
        if dbitem:
            return Level(dbitem['id'], dbitem['name'], dbitem['stars'])

    @classmethod
    def get(cls, id):
        dblevels = Level.levels.query(KeyConditionExpression=Key('id').eq(id))['Items']
        if len(dblevels) > 0:
            return Level.__map(dblevels[0])

    @classmethod
    def getAll(cls):
        levels = list()
        for level in Level.levels.scan()['Items']:
            levels.append(Level.__map(level))
        levels.sort(key=lambda level: level.id)
        return levels

    @classmethod
    def getByName(cls, name):
        dblevels = Level.levels.scan(FilterExpression=Attr('name').eq(name))['Items']
        if len(dblevels) > 0:
            return Level.__map(dblevels[0])


class User:
    users = boto3.resource('dynamodb').Table('awscert_user')

    def __init__(self, user_id, certification_level, voucher_code=None, attribuated_date=None, profile_update_date=None, gift_sent_date=None):
        self.user_id = user_id
        self.certification_level = certification_level
        self.voucher_code = voucher_code
        self.attribuated_date = None
        self.profile_update_date = None
        self.gift_sent_date = None
        if attribuated_date:
            self.attribuated_date = datetime.datetime.strptime(attribuated_date, "%d/%m/%Y").date()
        self.profile_update_date = None
        if profile_update_date:
            self.profile_update_date = datetime.datetime.strptime(profile_update_date, "%d/%m/%Y").date()
        if gift_sent_date:
            self.gift_sent_date = datetime.datetime.strptime(gift_sent_date, "%d/%m/%Y").date()

    def __str__(self):
        str_format = "user_id: " + self.user_id + \
            ", certification_level: " + self.certification_level
        if self.voucher_code:
            str_format += ", voucher_code: " + self.voucher_code
        else:
            str_format += ", no voucher code"
        if self.profile_update_date:
            str_format += ", profile_update_date: " + self.profile_update_date.strftime('%m/%d/%Y')
        else:
            str_format += ", certification not yet passed"
        if self.gift_sent_date:
            str_format += ", gift_sent_date: " + self.gift_sent_date.strftime('%m/%d/%Y')
        else:
            str_format += ", gift not yet sent"
        return str_format

    def add(self):
        User.users.put_item(Item={'user_id': self.user_id, 'certification_level': self.certification_level})
        return True

    def remove(self):
        if not self.voucher_code:
            User.users.delete_item(Key={'user_id': self.user_id})
            return True
        return False

    def attribuateVoucher(self, voucher):
        if not self.voucher_code and self.certification_level == voucher.certification_level:
            self.voucher_code = voucher.code
            self.attribuated_date = time.localtime()
            User.users.update_item(Key={'user_id': self.user_id},
                                   UpdateExpression='SET voucher_code = :voucher_code, attribuated_date = :attribuated_date',
                                   ExpressionAttributeValues={':voucher_code': self.voucher_code,
                                                                ':attribuated_date': self.attribuated_date.strftime('%m/%d/%Y')})
            return True
        return False

    def passesCertification(self, level):
        if not self.profile_update_date and level.id == self.certification_level and self.voucher_code:
            self.profile_update_date = time.strftime('%d/%m/%Y',time.localtime())
            User.users.update_item(Key={'user_id': self.user_id},
                                   UpdateExpression='SET profile_update_date = :profile_update_date',
                                   ExpressionAttributeValues={':profile_update_date': self.profile_update_date.strftime('%m/%d/%Y')})
            return True
        return False

    def sendGift(self):
        if self.profile_update_date and not self.gift_sent_date:
            self.gift_sent_date = time.strftime('%d/%m/%Y',time.localtime())
            User.users.update_item(Key={'user_id': self.user_id},
                                   UpdateExpression='SET gift_sent_date = :gift_sent_date',
                                   ExpressionAttributeValues={':gift_sent_date': self.gift_sent_date.strftime('%m/%d/%Y')})
            return True
        return False

    @classmethod
    def __map(cls, dbitem):
        if dbitem:
            voucher_code = None
            attribuated_date = None
            profile_update_date = None
            gift_sent_date = None
            if 'voucher_code' in dbitem:
                voucher_code = dbitem['voucher_code']
            if 'attribuated_date' in dbitem:
                attribuated_date = dbitem['attribuated_date']
            if 'profile_update_date' in dbitem:
                profile_update_date = dbitem['profile_update_date']
            if 'gift_sent_date' in dbitem:
                gift_sent_date = dbitem['gift_sent_date']

            return User(dbitem['user_id'], dbitem['certification_level'], voucher_code, attribuated_date, profile_update_date, gift_sent_date)

    @classmethod
    def get(cls, user_id):
        dbusers = User.users.query(KeyConditionExpression=Key('user_id').eq(user_id))['Items']
        if len(dbusers) > 0:
            return User.__map(dbusers[0])

    @classmethod
    def getAll(cls):
        users = list()
        for user in User.users.scan()['Items']:
            users.append(User.__map(user))
        return users


class Voucher:
    vouchers = boto3.resource('dynamodb').Table('awscert_voucher')

    def __init__(self, code, certification_level, availability):
        self.code = code
        self.certification_level = certification_level
        self.availability = datetime.datetime.strptime(availability, "%d/%m/%Y").date()

    def __str__(self):
        str_format = "Code: " + self.code + ", level: " + self.certification_level
        if self.isAvailable():
            str_format += ", available until " + self.availability.strftime('%m/%d/%Y')
        else:
            str_format += "already claimed by " + \
            User.users.scan(FilterExpression=Attr('voucher_code').eq(self.code))['Items'][0]['user_id']
        return str_format

    def add(self):
        Voucher.vouchers.put_item(Item={'code': self.code, 'certification_level': self.certification_level, 'availability': self.availability.strftime('%m/%d/%Y')})
        return True

    def remove(self):
        if self.isAvailable():
            Voucher.vouchers.delete_item(Key={'code': self.code})
            return True
        return False

    def isAvailable(self):
        return len(User.users.scan(FilterExpression=Attr('voucher_code').eq(self.code))['Items']) == 0

    @classmethod
    def __map(cls, dbitem):
        if dbitem:
            return Voucher(dbitem['code'], dbitem['certification_level'], dbitem['availability'])

    @classmethod
    def get(cls, code):
        dbvouchers = Voucher.vouchers.query(KeyConditionExpression=Key('code').eq(code))['Items']
        if len(dbvouchers) > 0:
            return Voucher.__map(dbvouchers[0])

    @classmethod
    def getAll(cls):
        vouchers = list()
        for voucher in Voucher.vouchers.scan()['Items']:
            vouchers.append(Voucher.__map(voucher))
        return vouchers

    @classmethod
    def getAvailable(cls, certification_level):
        vouchersdb = cls.vouchers.scan(FilterExpression=Attr('certification_level').eq(certification_level))['Items']
        for voucherdb in vouchersdb:
            voucher = Voucher(voucherdb['code'], voucherdb['certification_level'], voucherdb['availability'])
            if voucher.isAvailable():
                return voucher
        return None


class Milestone:
    milestones = boto3.resource('dynamodb').Table('awscert_milestone')

    def __init__(self, id, date, goal: int):
        self.id = id
        self.date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        self.goal = goal

    def __str__(self):
        return "Id: " + self.id + ", date: " + self.date.strftime('%m/%d/%Y') + ", goal: " + self.goal + " stars"

    @classmethod
    def __map(cls, dbitem):
        if dbitem:
            return Milestone(dbitem['id'], dbitem['date'], dbitem['goal'])

    @classmethod
    def getAll(cls):
        milestones = list()
        for milestone in Milestone.milestones.scan()['Items']:
            milestones.append(Milestone.__map(milestone))
        milestones.sort(key=lambda milestone: milestone.id)
        return milestones
