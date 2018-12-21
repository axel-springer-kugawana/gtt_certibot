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
            Certification.certifications.remove(self)
            return True
        return False

    @classmethod
    def get(cls, level):
        dbcertifications = Certification.certifications.scan(FilterExpression=Attr('level').eq(level))['Items']
        if len(dbcertifications) > 0:
            return Certification(dbcertifications[0]['name'], dbcertifications[0]['level'])


class User:
    users = boto3.resource('dynamodb').Table('awscert_user')

    def __init__(self, email, certification_level, voucher_code=None):
        self.email = email
        self.certification_level = certification_level
        self.voucher_code = voucher_code

    def __str__(self):
        str_format = "Email: " + self.email + \
            ", certification_level: " + self.certification_level
        if self.voucher_code:
            str_format += ", voucher_code: " + self.voucher_code
        else:
            str_format += ", no voucher code"
        return str_format

    def add(self):
        User.users.put_item(Item={'email': self.email, 'certification_level': self.certification_level})
        return True

    def remove(self):
        if not self.voucher_code:
            User.users.delete_item(Key={'email': self.email})
            return True
        return False

    def attribuateVoucher(self, voucher):
        if not self.voucher_code and self.certification_level == voucher.certification_level:
            self.voucher_code = voucher.code
            User.users.update_item(Key={'email': self.email},
                                   UpdateExpression='SET voucher_code = :voucher_code',
                                   ExpressionAttributeValues={':voucher_code': self.voucher_code})
            return True
        return False

    @classmethod
    def get(cls, email):
        dbusers = User.users.query(KeyConditionExpression=Key('email').eq(email))['Items']
        if len(dbusers) > 0:
            try:
                return User(dbusers[0]['email'], dbusers[0]['certification_level'], dbusers[0]['voucher_code'])
            except KeyError:
                return User(dbusers[0]['email'], dbusers[0]['certification_level'])


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
            User.users.scan(FilterExpression=Attr('voucher_code').eq(self.code))['Items'][0]['email']
        return str_format

    def add(self):
        Voucher.vouchers.put_item(Item={'code': self.code, 'certification_level': self.certification_level})
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
