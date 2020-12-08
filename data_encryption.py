from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import secrets

KEK_FILENAME = "kek.key"
NONCE_SIZE = 12


def generate_key():
    return ChaCha20Poly1305.generate_key()


def generate_nonce():
    return secrets.token_bytes(NONCE_SIZE)


def create_kek():
    with open(KEK_FILENAME, "wb") as f:
        f.write(generate_key())


def get_kek():
    with open(KEK_FILENAME, "rb") as f:
        return f.read()


def generate_dek():
    kek = get_kek()
    dek_nonce = generate_nonce()
    dek = generate_key()
    return (dek_nonce, ChaCha20Poly1305(kek).encrypt(dek_nonce, dek, None))


def encrypt(dek_nonce, encrypted_dek, data):
    kek = get_kek()
    dek = ChaCha20Poly1305(kek).decrypt(dek_nonce, encrypted_dek, None)
    data_nonce = generate_nonce()
    return (data_nonce, ChaCha20Poly1305(dek).encrypt(data_nonce, data, None))


def decrypt(dek_nonce, encrypted_dek, data_nonce, data):
    kek = get_kek()
    dek = ChaCha20Poly1305(kek).decrypt(dek_nonce, encrypted_dek, None)
    return ChaCha20Poly1305(dek).decrypt(data_nonce, data, None)