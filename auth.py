import sqlite3
import hashlib
import re
from database import DB_PATH

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_email(value):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", value))

def register_user(username, email, password, full_name, goal="Other"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Add goal column if not exists
    try:
        c.execute("ALTER TABLE users ADD COLUMN goal TEXT DEFAULT 'Other'")
        conn.commit()
    except:
        pass
    try:
        c.execute("""
            INSERT INTO users (username, email, password_hash, full_name, goal)
            VALUES (?, ?, ?, ?, ?)
        """, (username.lower(), email.lower(), hash_password(password), full_name, goal))
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken!"
        elif "email" in str(e):
            return False, "Email already registered!"
        return False, "Registration failed!"
    finally:
        conn.close()

def login_user(identifier, password):
    """Login with username OR email + password."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    identifier = identifier.lower().strip()
    pw_hash = hash_password(password)

    if is_email(identifier):
        c.execute("SELECT username, full_name, goal FROM users WHERE email=? AND password_hash=?",
                  (identifier, pw_hash))
    else:
        c.execute("SELECT username, full_name, goal FROM users WHERE username=? AND password_hash=?",
                  (identifier, pw_hash))

    row = c.fetchone()
    conn.close()
    if row:
        return True, {"username": row[0], "full_name": row[1], "goal": row[2] or "Other"}
    return False, "Invalid credentials!"

def get_user_profile(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, email, full_name, goal, created_at FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "email": row[1], "full_name": row[2],
                "goal": row[3], "joined": row[4]}
    return None
