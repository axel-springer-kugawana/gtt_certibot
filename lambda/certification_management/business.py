import time
import boto3
from boto3.dynamodb.conditions import Key, Attr


class Certification:
    certifications = boto3.resource('dynamodb').Table('awscert_certification')

    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __str__(self):
        return "Name: " + self.name + ", level: " + self.level

    def add(self):
        Certification.certifications.put_item(Item={'name': self.name, 'level': self.level})
        return True

    def remove(self):
        if len(Voucher.vouchers.scan(FilterExpression=Attr('certification_level').eq(self.level))['Items']) == 0 \
           and len(User.users.scan(FilterExpression=Attr('certification_level').eq(self.level))['Items']) == 0:
            Certification.certifications.delete_item(Key={'name': self.name})
            return True
        return False

    @classmethod
    def get(cls, level):
        dbcertifications = Certification.certifications.scan(FilterExpression=Attr('level').eq(level))['Items']
        if len(dbcertifications) > 0:
            return Certification(dbcertifications[0]['name'], dbcertifications[0]['level'])

    @classmethod
    def getByName(cls, name):
        dbcertifications = Certification.certifications.query(KeyConditionExpression=Key('name').eq(name))['Items']
        if len(dbcertifications) > 0:
            return Certification(dbcertifications[0]['name'], dbcertifications[0]['level'])


class User:
    users = boto3.resource('dynamodb').Table('awscert_user')

    def __init__(self, user_id, certification_level, voucher_code=None, attribuated_date=None, profil_update_date=None):
        self.user_id = user_id
        self.certification_level = certification_level
        self.voucher_code = voucher_code
        self.attribuated_date = attribuated_date
        self.profil_update_date = profil_update_date

    def __str__(self):
        str_format = "user_id: " + self.user_id + \
            ", certification_level: " + self.certification_level
        if self.voucher_code:
            str_format += ", voucher_code: " + self.voucher_code
        else:
            str_format += ", no voucher code"
        if self.profil_update_date:
            str_format += ", profil_update_date: " + self.profil_update_date
        else:
            str_format += ", certification not yet passed"
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
            self.attribuated_date = time.strftime('%d/%m/%Y',time.localtime())
            User.users.update_item(Key={'user_id': self.user_id},
                                   UpdateExpression='SET voucher_code = :voucher_code, attribuated_date = :attribuated_date',
                                   ExpressionAttributeValues={':voucher_code': self.voucher_code,
                                                                ':attribuated_date': self.attribuated_date})
            return True
        return False

    def passesCertification(self, certification):
        if not self.profil_update_date and certification.level == self.certification_level and self.voucher_code:
            self.profil_update_date = time.strftime('%d/%m/%Y',time.localtime())
            User.users.update_item(Key={'user_id': self.user_id},
                                   UpdateExpression='SET profil_update_date = :profil_update_date',
                                   ExpressionAttributeValues={':profil_update_date': self.profil_update_date})
            return True
        return False

    @classmethod
    def get(cls, user_id):
        dbusers = User.users.query(KeyConditionExpression=Key('user_id').eq(user_id))['Items']
        if len(dbusers) > 0:
            voucher_code = None
            attribuated_date = None
            profil_update_date = None
            if 'voucher_code' in dbusers[0]:
                voucher_code = dbusers[0]['voucher_code']
            if 'attribuated_date' in dbusers[0]:
                attribuated_date = dbusers[0]['attribuated_date']
            if 'profil_update_date' in dbusers[0]:
                profil_update_date = dbusers[0]['profil_update_date']

            return User(dbusers[0]['user_id'], dbusers[0]['certification_level'], voucher_code, attribuated_date, profil_update_date)


class Voucher:
    vouchers = boto3.resource('dynamodb').Table('awscert_voucher')

    def __init__(self, code, certification_level, availability):
        self.code = code
        self.certification_level = certification_level
        self.availability = availability

    def __str__(self):
        str_format = "Code: " + self.code + ", level: " + self.certification_level
        if self.isAvailable():
            str_format += ", available until " + self.availability
        else:
            str_format += "already claimed by " + \
            User.users.scan(FilterExpression=Attr('voucher_code').eq(self.code))['Items'][0]['user_id']
        return str_format

    def add(self):
        Voucher.vouchers.put_item(Item={'code': self.code, 'certification_level': self.certification_level, 'availability': self.availability})
        return True

    def remove(self):
        if self.isAvailable():
            Voucher.vouchers.delete_item(Key={'code': self.code})
            return True
        return False

    def isAvailable(self):
        return len(User.users.scan(FilterExpression=Attr('voucher_code').eq(self.code))['Items']) == 0

    @classmethod
    def get(cls, code):
        dbvouchers = Voucher.vouchers.query(KeyConditionExpression=Key('code').eq(code))['Items']
        if len(dbvouchers) > 0:
            return Voucher(dbvouchers[0]['code'], dbvouchers[0]['certification_level'], dbvouchers[0]['availability'])

    @classmethod
    def getAvailable(cls, certification_level):
        vouchersdb = cls.vouchers.scan(FilterExpression=Attr('certification_level').eq(certification_level))['Items']
        for voucherdb in vouchersdb:
            voucher = Voucher(voucherdb['code'], voucherdb['certification_level'], voucherdb['availability'])
            if voucher.isAvailable():
                return voucher
        return None
