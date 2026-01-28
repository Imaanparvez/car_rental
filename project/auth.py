from db import users_col
import bcrypt
from bson import ObjectId

def register_user(name, email, phone, password):
    # Check if user exists
    if users_col.find_one({"email": email}):
        return False

    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Create new user
    result = users_col.insert_one({
        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed  # stored as bytes (standard)
    })

    return True


def login_user(email, password):
    user = users_col.find_one({"email": email})
    
    if not user:
        return None

    # Validate password
    if not bcrypt.checkpw(password.encode(), user["password"]):
        return None
    
    # ✔ Return only SAFE values
    return {
        "_id": str(user["_id"]),      # string version
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"]
        # Do NOT return the hashed password
    }
