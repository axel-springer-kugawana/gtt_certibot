import certification_management


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
            str_format += "already claimed by " + \
                ", ".join(
                    [user.email for user in User.users if user.voucher_code == self.code])
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
