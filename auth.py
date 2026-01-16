from db import users_col
import bcrypt

def register_user(name, email, phone, password):
    if users_col.find_one({"email": email}):
        return False

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    users_col.insert_one({
        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed
    })
    return True

def login_user(email, password):
    user = users_col.find_one({"email": email})
    if not user:
        return None

    if bcrypt.checkpw(password.encode(), user["password"]):
        return user

    return None
