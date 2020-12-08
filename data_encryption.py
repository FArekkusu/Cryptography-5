from cryptography.fernet import Fernet

KEK_FILENAME = "kek.key"


def generate_key():
    return Fernet.generate_key()


def create_kek():
    with open(KEK_FILENAME, "wb") as f:
        f.write(generate_key())


def get_kek():
    with open(KEK_FILENAME, "rb") as f:
        return f.read()


def generate_dek():
    dek = generate_key()
    kek = get_kek()
    return Fernet(kek).encrypt(dek)


def encrypt(encrypted_dek, data):
    kek = get_kek()
    dek = Fernet(kek).decrypt(encrypted_dek)
    return Fernet(dek).encrypt(data)


def decrypt(encrypted_dek, data):
    kek = get_kek()
    dek = Fernet(kek).decrypt(encrypted_dek)
    return Fernet(dek).decrypt(data)