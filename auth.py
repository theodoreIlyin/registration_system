import re
import os 
import hashlib
from datetime import datetime

import database 
import state

def hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode("utf-8"),salt, 100_000)
    return salt.hex(), h.hex()


def normalize_phone(phone):
    return re.sub(r'[^\d+]', "", phone)

def vali