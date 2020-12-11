from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime
import os

KEY_PATH = os.path.join("tls", "key.pem")
CERT_PATH = os.path.join("tls", "cert.pem")
PASSPHRASE = b"passphrase"


def generate_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )


def generate_certificate(key):
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "UA"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Kyiv oblast"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Kyiv"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
        x509.NameAttribute(NameOID.COMMON_NAME, "mysite.com"),
    ])

    now = datetime.datetime.utcnow()

    return (x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=10))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False,)
        .sign(key, hashes.SHA256()))


def create_key_cert_pair():
    if not os.path.exists("tls"):
        os.makedirs("tls")

    key = generate_key()
    cert = generate_certificate(key)

    with open(KEY_PATH, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(PASSPHRASE),
        ))

    with open(CERT_PATH, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))