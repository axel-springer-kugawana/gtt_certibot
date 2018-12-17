class Certification:
    certifications = list()

    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __str__(self):
        return "Name: " + self.name + ", level: " + self.level

    def add(self):
        Certification.certifications.append(self)
        return True

    def remove(self):
        if self.level not in [voucher.level for voucher in Voucher.vouchers] \
        and self.level not in [user.level for user in User.users]:
            Certification.certifications.remove(self)
            return True
        return False

    @classmethod
    def reset_cascade(cls):
        cls.certifications = list()
        Voucher.vouchers = list()
        User.users = list()
        return True


class Voucher:
    vouchers = list()

    def __init__(self, code, certification_level):
        self.code = code
        self.certification_level = certification_level

    def __str__(self):
        str_format = "Code: " + self.code + ", level: " + self.certification_level
        if self.isAvailable:
            str_format += ", available"
        else:
            str_format += "already claimed by " + ", ".join([user.email for user in User.users if user.voucher_code == self.code])
        return str_format

    def add(self):
        Voucher.vouchers.append(self)
        return True

    def remove(self):
        if self.isAvailable:
            Voucher.vouchers.remove(self)
            return True
        return False

    def isAvailable(self):
        return self.code not in [user.voucher_code for user in User.users]


class User:
    users = list()

    def __init__(self, email, certification_level, voucher_code=None):
        self.email = email
        self.certification_level = certification_level
        self.voucher_code = voucher_code

    def __str__(self):
        str_format = "Email: " + self.email + ", certification_level: " + self.certification_level
        if self.voucher_code:
            str_format += ", voucher_code: " + self.voucher_code
        else:
            str_format += ", no voucher code"
        return str_format

    def add(self):
        User.users.append(self)

    def remove(self):
        if not self.voucher_code:
            User.users.remove(self)
            return True
        return False

    def give_voucher(self, voucher: Voucher):
        if not self.voucher_code and voucher.isAvailable():
            self.voucher_code = voucher.code
