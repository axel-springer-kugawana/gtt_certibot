import boto3
import datetime
import time
from boto3.dynamodb.conditions import Key, Attr


class Certification:
    certifications = boto3.resource('dynamodb').Table('certibot_certification')

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return "Id: " + self.id + ", name: " + self.name

    def add(self):
        Certification.certifications.put_item(Item={'id': self.id, 'name': self.name})
        return True

    def remove(self):
        if len(Level.getByCertification(self.id)) == 0:
            Certification.certifications.delete_item(Key={'id': self.id})
            return True
        return False

    @classmethod
    def __map(cls, dbitem):
        if dbitem:
            return Certification(dbitem['id'], dbitem['name'])

    @classmethod
    def get(cls, id):
        dbcertifications = Certification.certifications.query(KeyConditionExpression=Key('id').eq(id))['Items']
        if len(dbcertifications) > 0:
            return Level.__map(dbcertifications[0])

    @classmethod
    def getAll(cls):
        certifications = list()
        for certification in Certification.certifications.scan()['Items']:
            certifications.append(Certification.__map(certification))
        certifications.sort(key=lambda certification: certification.id)
        return certifications


class Level:
    levels = boto3.resource('dynamodb').Table('certibot_level')

    def __init__(self, id, name, stars, certification_id):
        self.id = id
        self.name = name
        self.certification_id = certification_id
        self.stars = stars

    def __str__(self):
        return "Id: " + str(self.id) + ", name: " + self.name + ", certification_id: " + str(self.certification_id) + ", stars: " + str(self.stars)

    def add(self):
        Level.levels.put_item(Item={'id': self.id, 'name': self.name, 'certification_id': self.certification_id, 'stars': self.stars})
        return True

    def remove(self):
        if len(Voucher.getByLevel(self.id)) == 0 \
           and len(UserCertification.getByLevel(self.id)) == 0:
            Level.levels.delete_item(Key={'id': self.id})
            return True
        return False

    @classmethod
    def __map(cls, dbitem):
        if dbitem:
            return Level(dbitem['id'], dbitem['name'], dbitem['stars'], dbitem['certification_id'])

    @classmethod
    def get(cls, id):
        dblevels = Level.levels.query(KeyConditionExpression=Key('id').eq(id))['Items']
        if len(dblevels) > 0:
            return Level.__map(dblevels[0])

    @classmethod
    def getAll(cls):
        levels = list()
        for dblevel in Level.levels.scan()['Items']:
            levels.append(Level.__map(dblevel))
        levels.sort(key=lambda level: level.id)
        return levels

    @classmethod
    def getByName(cls, name):
        dblevels = Level.levels.scan(FilterExpression=Attr('name').eq(name))['Items']
        if len(dblevels) > 0:
            return Level.__map(dblevels[0])

    @classmethod
    def getByCertification(cls, certification_id):
        dblevels = Level.levels.scan(FilterExpression=Attr('certification_id').eq(certification_id))['Items']
        return [Level.__map(dblevel) for dblevel in dblevels]


class User:
    def __init__(self, id, user_certifications=None):
        self.id = id
        self.user_certifications = user_certifications

    def __str__(self):
        return "id: " + self.id

    def formatSlackFields(self):
        fields = list()
        voucher_infos = "Voucher code: "
        for user_certification in self.user_certifications:
            if user_certification.voucher_code:
                voucher_infos = user_certification.voucher_code \
                    + "\n_valid until " \
                    + Voucher.get(user_certification.voucher_code).availability.strftime('%d/%m/%Y') \
                    + "_"
            else:
                voucher_infos = "_not yet requested_"

            field_dict = {}
            field_dict["type"] = "mrkdwn"
            field_dict["text"] = "*" + Level.get(user_certification.level_id).name + "*\n" + voucher_infos
            fields.append(field_dict)
        return fields

    @classmethod
    def get(cls, id):
        user_certifications = UserCertification.get(id)
        if user_certifications:
            return User(id, user_certifications)


class UserCertification:
    users_certifications = boto3.resource('dynamodb').Table('certibot_user_certification')

    def __init__(self, user_id, level_id, voucher_code=None, attribuated_date=None, profile_update_date=None, gift_sent_date=None):
        self.user_id = user_id
        self.level_id = level_id
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
            ", level_id: " + self.level_id
        if self.voucher_code:
            str_format += ", voucher_code: " + self.voucher_code
        else:
            str_format += ", no voucher code"
        if self.profile_update_date:
            str_format += ", profile_update_date: " + self.profile_update_date.strftime('%d/%m/%Y')
        else:
            str_format += ", certification not yet passed"
        if self.gift_sent_date:
            str_format += ", gift_sent_date: " + self.gift_sent_date.strftime('%d/%m/%Y')
        else:
            str_format += ", gift not yet sent"
        return str_format

    def add(self):
        UserCertification.users_certifications.put_item(Item={'user_id': self.user_id, 'level_id': self.level_id})
        return True

    def remove(self):
        if not self.voucher_code:
            UserCertification.users_certifications.delete_item(Key={'user_id': self.user_id, 'level_id': self.level_id})
            return True
        return False

    def attribuateVoucher(self, voucher):
        if not self.voucher_code and self.level_id == voucher.level_id:
            self.voucher_code = voucher.code
            self.attribuated_date = datetime.datetime.now()
            UserCertification.users_certifications.update_item(Key={'user_id': self.user_id, 'level_id': self.level_id},
                                   UpdateExpression='SET voucher_code = :voucher_code, attribuated_date = :attribuated_date',
                                   ExpressionAttributeValues={':voucher_code': self.voucher_code,
                                                                ':attribuated_date': self.attribuated_date.strftime('%d/%m/%Y')})
            return True
        return False

    def passesCertification(self, level):
        if not self.profile_update_date and level.id == self.level_id and self.voucher_code:
            self.profile_update_date = datetime.datetime.now()
            UserCertification.users_certifications.update_item(Key={'user_id': self.user_id, 'level_id': self.level_id},
                                   UpdateExpression='SET profile_update_date = :profile_update_date',
                                   ExpressionAttributeValues={':profile_update_date': self.profile_update_date.strftime('%d/%m/%Y')})
            return True
        return False

    def sendGift(self):
        if self.profile_update_date and not self.gift_sent_date:
            self.gift_sent_date = datetime.datetime.now()
            UserCertification.users_certifications.update_item(Key={'user_id': self.user_id, 'level_id': self.level_id},
                                   UpdateExpression='SET gift_sent_date = :gift_sent_date',
                                   ExpressionAttributeValues={':gift_sent_date': self.gift_sent_date.strftime('%d/%m/%Y')})
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

            return UserCertification(dbitem['user_id'], dbitem['level_id'], voucher_code, attribuated_date, profile_update_date, gift_sent_date)

    @classmethod
    def get(cls, user_id):
        dbusers = UserCertification.users_certifications.query(KeyConditionExpression=Key('user_id').eq(user_id))['Items']
        return [UserCertification.__map(dbuser) for dbuser in dbusers]

    @classmethod
    def getAll(cls):
        dbusers = UserCertification.users_certifications.scan()['Items']
        return [UserCertification.__map(dbuser) for dbuser in dbusers]

    @classmethod
    def getByLevel(cls, level_id):
        dbusers = UserCertification.users_certifications.scan(FilterExpression=Attr('level_id').eq(level_id))['Items']
        return [UserCertification.__map(dbuser) for dbuser in dbusers]

    @classmethod
    def getByVoucher(cls, voucher_code):
        dbusers = UserCertification.users_certifications.scan(FilterExpression=Attr('voucher_code').eq(voucher_code))['Items']
        return [UserCertification.__map(dbuser) for dbuser in dbusers]


class Voucher:
    vouchers = boto3.resource('dynamodb').Table('certibot_voucher')

    def __init__(self, code, level_id, availability):
        self.code = code
        self.level_id = level_id
        self.availability = datetime.datetime.strptime(availability, "%d/%m/%Y").date()

    def __str__(self):
        str_format = "Code: " + self.code + ", level_id: " + self.level_id
        if self.isAvailable():
            str_format += ", available until " + self.availability.strftime('%d/%m/%Y')
        else:
            str_format += "already claimed by " + \
            UserCertification.users_certifications.scan(FilterExpression=Attr('voucher_code').eq(self.code))['Items'][0]['user_id']
        return str_format

    def add(self):
        Voucher.vouchers.put_item(Item={'code': self.code, 'level_id': self.level_id, 'availability': self.availability.strftime('%d/%m/%Y')})
        return True

    def remove(self):
        if self.isAvailable():
            Voucher.vouchers.delete_item(Key={'code': self.code})
            return True
        return False

    def isAvailable(self):
        return len(UserCertification.getByVoucher(self.code)) == 0

    @classmethod
    def __map(cls, dbitem):
        if dbitem:
            return Voucher(dbitem['code'], dbitem['level_id'], dbitem['availability'])

    @classmethod
    def get(cls, code):
        dbvouchers = Voucher.vouchers.query(KeyConditionExpression=Key('code').eq(code))['Items']
        if len(dbvouchers) > 0:
            return Voucher.__map(dbvouchers[0])

    @classmethod
    def getAll(cls):
        dbVouchers = Voucher.vouchers.scan()['Items']
        return [Voucher.__map(dbvoucher) for dbvoucher in dbVouchers]

    @classmethod
    def getAvailable(cls, level_id):
        vouchersdb = cls.vouchers.scan(FilterExpression=Attr('level_id').eq(level_id))['Items']
        for voucherdb in vouchersdb:
            voucher = Voucher(voucherdb['code'], voucherdb['level_id'], voucherdb['availability'])
            if voucher.isAvailable():
                return voucher
        return None

    @classmethod
    def getByLevel(cls, level_id):
        dbVouchers = Voucher.vouchers.scan(FilterExpression=Attr('level_id').eq(level_id))['Items']
        return [Voucher.__map(dbvoucher) for dbvoucher in dbVouchers]


class Milestone:
    milestones = boto3.resource('dynamodb').Table('certibot_milestone')

    def __init__(self, id, date, goal: int):
        self.id = id
        self.date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        self.goal = goal

    def __str__(self):
        return "Id: " + self.id + ", date: " + self.date.strftime('%d/%m/%Y') + ", goal: " + self.goal + " stars"

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
