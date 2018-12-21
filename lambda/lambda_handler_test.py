from fake_data import init_fake_data
from lambda_handler import handler
import json
from certification_management.business import *

# For test purpose, to be moved to a real database
init_fake_data()

User("userdb@fake.data", "lvl1")
Certification("certdb", "lvl1")
Voucher("codedb", "lvl1")
