import sqlite3
import exceptions
from password_hashing import get_hash, verify_hash, needs_rehash

DATABASE = "users.db"
CREATE = "CREATE TABLE IF NOT EXISTS credentials (id INTEGER PRIMARY KEY, email TEXT, password_hash TEXT, version INTEGER);"
DROP = "DROP TABLE IF EXISTS credentials;"
SELECT_BY_EMAIL = "SELECT * FROM credentials WHERE email = ?;"
INSERT_CREDENTIALS = "INSERT INTO credentials (email, password_hash, version) VALUES (?, ?, ?)"
UPDATE_PASSWORD = "UPDATE credentials SET password_hash = ? WHERE email = ?"

MIN_PASSWORD_LENGTH = 16
CURRENT_PASSWORD_VERSION = 1


def create():
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    con.execute(CREATE)
    con.commit()

    cursor.close()
    con.close()


def drop():
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    con.execute(DROP)
    con.commit()

    cursor.close()
    con.close()


def register(email, password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise exceptions.PasswordTooShortError
    if password.casefold() in (email.casefold(), email.split("@")[0].casefold()):
        raise exceptions.EmailMatchesPasswordError

    hash = get_hash(password)

    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    try:
        cursor.execute(SELECT_BY_EMAIL, (email,))
        if cursor.fetchone() is not None:
            return

        cursor.execute(INSERT_CREDENTIALS, (email, hash, CURRENT_PASSWORD_VERSION))
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
            verify_hash(password, record[2])
        except Exception:
            raise exceptions.InvalidCredentialsError
        
        if record[3] < CURRENT_PASSWORD_VERSION:
            raise exceptions.OutdatedPasswordVersionError
        
        if needs_rehash(record[2]):
            hash = get_hash(password)
            cursor.execute(UPDATE_PASSWORD, (hash, email))
            con.commit()
    finally:
        cursor.close()
        con.close()