import argon2
import hashlib
import sqlite3
import exceptions

DATABASE = "users.db"
CREATE = "CREATE TABLE IF NOT EXISTS credentials (id INTEGER PRIMARY KEY, email TEXT, password_hash TEXT);"
DROP = "DROP TABLE IF EXISTS credentials;"
SELECT_BY_EMAIL = "SELECT * FROM credentials WHERE email = ?;"
INSERT_CREDENTIALS = "INSERT INTO credentials (email, password_hash) VALUES (?, ?)"
UPDATE_PASSWORD = "UPDATE credentials SET password_hash = ? WHERE email = ?"

MIN_PASSWORD_LENGTH = 16
PASSWORD_HASHER = argon2.PasswordHasher()

def create():
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    con.execute(CREATE)
    con.commit()

    cursor.close()
    con.close()

def register(email, password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise exceptions.PasswordTooShortError

    sha512_hash = hashlib.sha512(bytes(password, encoding="utf-8")).hexdigest()
    argon2_hash = PASSWORD_HASHER.hash(sha512_hash)

    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    try:
        cursor.execute(SELECT_BY_EMAIL, (email,))
        if cursor.fetchone() is not None:
            return

        cursor.execute(INSERT_CREDENTIALS, (email, argon2_hash))
        con.commit()
    finally:
        cursor.close()
        con.close()

def login(email, password):
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    try:
        cursor.execute(SELECT_BY_EMAIL, (email,))
        record = cursor.fetchone()

        try:
            sha512_hash = hashlib.sha512(bytes(password, encoding="utf-8")).hexdigest()
            PASSWORD_HASHER.verify(record[2], sha512_hash)
        except Exception:
            raise exceptions.InvalidCredentialsError
        
        if PASSWORD_HASHER.check_needs_rehash(record[2]):
            argon2_hash = PASSWORD_HASHER.hash(sha512_hash)
            cursor.execute(UPDATE_PASSWORD, (argon2_hash, email))
            con.commit()
    finally:
        cursor.close()
        con.close()