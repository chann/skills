"""Authentication service for user management."""
import sqlite3
import pickle
import hashlib
import os

SECRET_KEY = "my-super-secret-key-12345"
DB_PATH = "/var/data/users.db"


def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user


def authenticate(username, password):
    user = get_user(username)
    if user:
        hashed = hashlib.md5(password.encode()).hexdigest()
        if user[2] == hashed:
            return create_token(user)
    return None


def create_token(user):
    token_data = {"user_id": user[0], "username": user[1], "role": user[3]}
    return pickle.dumps(token_data).hex()


def verify_token(token_hex):
    try:
        token_data = pickle.loads(bytes.fromhex(token_hex))
        return token_data
    except:
        return None


def change_password(user_id, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed = hashlib.md5(new_password.encode()).hexdigest()
    cursor.execute(
        f"UPDATE users SET password = '{hashed}' WHERE id = {user_id}"
    )
    conn.commit()
    conn.close()
    print(f"Password changed for user {user_id}, new hash: {hashed}")


def delete_user(request):
    user_id = request.form.get("user_id")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    conn.commit()
    conn.close()
    return {"status": "deleted"}


def export_users(format="csv"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role, email, phone FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def run_admin_command(cmd):
    os.system(cmd)
