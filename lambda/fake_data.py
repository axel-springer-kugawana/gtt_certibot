from certification_managment import *


def init_fake_data():
    Certification.reset_cascade()

    Certification("Certif 1", "Level 1").add()
    Certification("Certif 2", "Level 2").add()
    Certification("Certif 3", "Level 3").add()

    Voucher("1000", "Level 1").add()
    Voucher("1001", "Level 1").add()
    Voucher("1002", "Level 1").add()
    Voucher("1003", "Level 1").add()
    Voucher("2000", "Level 2").add()
    Voucher("2001", "Level 2").add()
    Voucher("2002", "Level 2").add()
    Voucher("2003", "Level 2").add()
    Voucher("3000", "Level 3").add()
    Voucher("3001", "Level 3").add()
    Voucher("3002", "Level 3").add()
    Voucher("3003", "Level 3").add()

    User("user10@fake.data", "Level 1").add()
    User("user11@fake.data", "Level 1").add()
    User("user12@fake.data", "Level 1").add()
    User("user13@fake.data", "Level 1").add()
    User("user14@fake.data", "Level 1").add()
    User("user20@fake.data", "Level 2").add()
    User("user21@fake.data", "Level 2").add()
    User("user22@fake.data", "Level 2").add()
    User("user23@fake.data", "Level 2").add()
    User("user24@fake.data", "Level 2").add()
    User("user30@fake.data", "Level 3").add()
    User("user31@fake.data", "Level 3").add()
    User("user32@fake.data", "Level 3").add()
    User("user33@fake.data", "Level 3").add()
    User("user34@fake.data", "Level 3").add()
