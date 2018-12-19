import certification_management


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

    def removeCertification(self):
        if self.level not in [voucher.level for voucher in Voucher.vouchers] \
                and self.level not in [user.level for user in User.users]:
            Certification.certifications.remove(self)
            return True
        return False
