import sqlite3
import exceptions
import password_hashing
import data_encryption

DATABASE = "users.db"

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    version INTEGER NOT NULL,

    data_encryption_key_nonce BLOB NOT NULL,
    data_encryption_key BLOB NOT NULL,
    data_nonce BLOB NOT NULL,
    biography BLOB NOT NULL
);
"""
DROP_USERS = "DROP TABLE IF EXISTS users;"
SELECT_ALL_USERS = "SELECT * FROM users;"
SELECT_USER_BY_EMAIL = "SELECT * FROM users WHERE email = ?;"
INSERT_USER = """
INSERT INTO users (email, password_hash, version, data_encryption_key_nonce, data_encryption_key, data_nonce, biography)
VALUES (?, ?, ?, ?, ?, ?, ?);
"""
UPDATE_USER_PASSWORD = "UPDATE users SET password_hash = ? WHERE email = ?;"
UPDATE_USER_BIOGRAPHY = "UPDATE users SET data_nonce = ?, biography = ? WHERE email = ?;"

MIN_PASSWORD_LENGTH = 16
CURRENT_PASSWORD_VERSION = 1


def create():
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    con.execute(CREATE_USERS)
    con.commit()

    cursor.close()
    con.close()


def drop():
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    con.execute(DROP_USERS)
    con.commit()

    cursor.close()
    con.close()


def register(email, password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise exceptions.PasswordTooShortError
    if password.casefold() in (email.casefold(), email.split("@")[0].casefold()):
        raise exceptions.EmailMatchesPasswordError

    hash = password_hashing.get_hash(password)

    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    try:
        cursor.execute(SELECT_USER_BY_EMAIL, (email,))
        if cursor.fetchone() is not None:
            return
        
        dek_nonce, dek = data_encryption.generate_dek()
        data_nonce, biography = data_encryption.encrypt(dek_nonce, dek, b"")

        cursor.execute(INSERT_USER, (email, hash, CURRENT_PASSWORD_VERSION, dek_nonce, dek, data_nonce, biography))
        con.commit()
    finally:
        cursor.close()
        con.close()


def login(email, password):
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    try:
        cursor.execute(SELECT_USER_BY_EMAIL, (email,))
        record = cursor.fetchone()

        try:
            password_hashing.verify_hash(password, record[2])
        except Exception:
            raise exceptions.InvalidCredentialsError
        
        if record[3] < CURRENT_PASSWORD_VERSION:
            raise exceptions.OutdatedPasswordVersionError
        
        if password_hashing.needs_rehash(record[2]):
            hash = password_hashing.get_hash(password)
            cursor.execute(UPDATE_USER_PASSWORD, (hash, email))
            con.commit()
    finally:
        cursor.close()
        con.close()


def set_biography(email, password, biography):
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    try:
        cursor.execute(SELECT_USER_BY_EMAIL, (email,))
        record = cursor.fetchone()

        try:
            password_hashing.verify_hash(password, record[2])
        except Exception:
            raise exceptions.InvalidCredentialsError
        
        data_nonce, encrypted_biography = data_encryption.encrypt(record[4], record[5], biography.encode())

        cursor.execute(UPDATE_USER_BIOGRAPHY, (data_nonce, encrypted_biography, email))
        con.commit()
    finally:
        cursor.close()
        con.close()


def get_users():
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    try:
        cursor.execute(SELECT_ALL_USERS)
        users = cursor.fetchall()
        return [
            (record[1], data_encryption.decrypt(record[4], record[5], record[6], record[7]).decode(), record[7])
            for record in users
        ]
    finally:
        cursor.close()
        con.close()
