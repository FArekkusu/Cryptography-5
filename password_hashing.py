import argon2
import hashlib
import exceptions

PASSWORD_HASHER = argon2.PasswordHasher()


def get_hash(password):
    sha512_hash = hashlib.sha512(bytes(password, encoding="utf-8")).hexdigest()
    return PASSWORD_HASHER.hash(sha512_hash)


def verify_hash(password, hash):
    sha512_hash = hashlib.sha512(bytes(password, encoding="utf-8")).hexdigest()
    PASSWORD_HASHER.verify(hash, sha512_hash)
    

def needs_rehash(hash):
    return PASSWORD_HASHER.check_needs_rehash(hash)