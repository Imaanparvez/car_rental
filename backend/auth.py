from db import users_col
import bcrypt


def register_user(name, email, phone, password):
    existing_user = users_col.find_one({"email": email})
    if existing_user:
        return False

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    users_col.insert_one({
        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed_password
    })

    return True


def login_user(email, password):
    user = users_col.find_one({"email": email})

    if not user:
        return None

    stored_password = user["password"]

    if bcrypt.checkpw(password.encode("utf-8"), stored_password):
        return user

    return None