import sqlite3
import bcrypt

def hash_password(plain_password):
    """平文のパスワードをハッシュ化"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt)

def check_password(plain_password, hashed_password):
    """平文のパスワードをハッシュと突合"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def register_user(username, plain_password, db_path='shopping_cart.db'):
    """ユーザーをデータベースに登録"""
    hashed_password = hash_password(plain_password)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute('INSERT INTO members (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        print(f"User {username} registered successfully!")
    except sqlite3.IntegrityError:
        print(f"Error: Username {username} already exists.")
    finally:
        conn.close()
