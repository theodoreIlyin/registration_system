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

def validate_registration(name, email, phone, password, password2):
    if not name:
        return "Введите имя"
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return 'Некорректная почта'
    if not re.fullmatch(r"\+?\d{10,13}", phone):
         return 'Некорректный телефон'
    if len(password) < 6:
        return 'Пароль миниум 6 символов'
    if password !=  password2:
        return "Пароль не верный"
    return None

def register_user(name, email, phone, password):
    salt, pwd_hash = hash_password(password)
    database.users_collection.insert_one({
        "name": name,
        "email": email,
        "phone": phone,
        "salt": salt,
        "password_hash": pwd_hash,
        "created_at": datetime.now(),
    })

def authenticate(login, password):
    login = login.strip().lower()
    user = database.users_collection.find_one(
        {"$or": [{"email": login}, {"phone": normalize_phone(login)}]}
    )
    if user:
        _, check = hash_password(password, bytes.fromhex(user["salt"]))
        if check ==  user['password_hash']:
            return user 
        return None

def login(user):
    state.current_user = user

def logout():
    state.current_user = None