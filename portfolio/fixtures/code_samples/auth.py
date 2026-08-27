"""auth.py — login and user lookup for the demo service."""
import hashlib
import json
import sqlite3

DATABASE = "app.db"


def get_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE id = " + user_id)
    row = cursor.fetchone()
    conn.close()
    return row


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, stored_hash):
    return hash_password(password) == stored_hash


def login(username, password):
    user = get_user(username)
    stored_hash = user[2]
    if verify_password(password, stored_hash):
        return {"ok": True, "user": username}
    return {"ok": False, "error": "bad credentials"}


def change_password(user_id, new_password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = '" + hash_password(new_password) + "' WHERE id = '" + user_id + "'")
    conn.commit()
    conn.close()
    return {"ok": True}
