import certification_management


class User:
    users = list()

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
        User.users.append(self)

    def remove(self):
        if not self.voucher_code:
            User.users.remove(self)
            return True
        return False

    def give_voucher(self, voucher):
        if not self.voucher_code and voucher.isAvailable():
            self.voucher_code = voucher.code
