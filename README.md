# Cryptography-5-7

This repository includes a simple server application showcasing:
* secure user registration and login;
* secure data storage;
* TLS configuration.

Flask web framework is used as the basis for the server, i.e. for serving HTML pages and processing the requests. TLS is also configured on the server directly. All the other logic is implemented manually.

## Secure user registration and login

### Password storage

Instead of storing the passwords directly, they're hashed using the SHA-512 and Argon2 algorithms, and the result is then saved in the database. SHA-512 is used first to "normalize" the password regardless of how long it is. Then the previously-calculated hash is passed as the input to Argon2 working in `id` mode, which is cryptographically secure, resistant to side-channel attacks, and resistant to GPU cracking attacks.

Although, this is not implemented in this example, for higher security the final password hashes could be further encrypted by a secure encryption algorithm, e.g. ChaCha20-Poly1305, XSalsa20-Poly1305, or AES-Poly1305. Such solution comes with a couple serious implications, though: you must store the encryption key in a secure way, inaccessible to potential attackers; losing the encryption key is equivalent to losing all the users' passwords' hashes as it would not be possible to decrypt them anymore.

### Registration

When the user tries to register, the password is immediately checked to have a minimum length of 16 characters, which should be secure enough for non-sensitive data at the time of this writing. After that, it is checked that the user is not trying to use the provided email address for password - either fully, or without the domain part. If either check fails, the registration routine fails as well, and the user is presented with a corresponding error message.

The password is hashed regardless of the fact whether another user with the same email already exists to prevent timing attacks. If the email address is unique, a new record is added to the database. In the end, a generic response is sent to the user saying that an activation link was sent to the provided email address (this message serves only as a confirmation that the registration routine finished successfully, there is no logic for actual email-sending implemented here) - this way a potential attacker cannot learn whether a new user was registered or not.

### Login

When the user tries to log in, a database record is fetched based on the provided email address, and it is verified that the stored Argon2 hash was computed from the SHA-512 hash of the provided password. If no record with the provided email address exists in the database, or the password verification fails, the user receives an error message about invalid credentials with no indication which step of the routine resulted in failure.

## Secure data storage

### Algorithm used

Data encryption and decryption is done using ChaCha20-Poly1305. The ChaCha20 stream cipher was selected because at the time of this writing it is considered to be one of the most secure cipher algorithms, on par with or better than Salsa20, which it is based on, and AES. The Poly1305 MAC is used because it provides message authenticity and integrity, it is practically as secure as the cipher it is used with, and is very efficient. Using a MAC is not required for secure data storage as the goal is to hide the data from everybody instead of making sure that the receivers can verify the data's authenticity, but it is built into the encryption function provided by the [library used for this project](https://github.com/pyca/cryptography) which is the reason it is used here.

### Data storage

This server uses envelope encryption for secure data storage. Such approach is good for a few reasons:
* apart from encrypting the users' data, the key used is encrypted too, providing one more layer of protection;
* the users' data, and keys can be encrypted using different algorithms, combining their individual strengths;
* It is easier to rotate/replace keys when they have to re-encrypt relatively short keys rather than potentially huge amounts of data;
* it is easier to decrypt a short key using a key management service (KMS) or a hardware security module (HSM), and encrypt/decrypt the data locally than transfer potentially huge amounts of data back and forth for encryption/decryption.

Firstly, a random key which will later be used as a Key Encryption Key (KEK) is generated, and saved to a local file. Storing KEK locally is the least secure option, and it is done here only for simplicity; for highest security one should use: physical/virtual HSM, or a trusted key management service, which also make it easier to generate, rotate, and replace keys when needed.

When a new user registers in the system, a random key which will later be used as a Data Encryption Key (DEK) is generated, encrypted using the aforementioned KEK, and then saved in the database where the users' credentials and data also reside. Anytime the user wants to access existing data, or store new data, this DEK will be decrypted using the KEK first, and then used for data encryption/decryption.

### Possible attack vectors

At the time of this writing there're no published attacks on ChaCha20 which means it is presumably not possible for an attacker to decrypt the data without gaining the access to the master key. In this project that is possible as the KEK is stored in a local file, and in case the attacker manages to get into the system, they might be able to access that file - whether they can actually read its contents depends on how the file permissions are configured, and whether the attacker has got root access, though. If, on the other hand, the master key was stored in an HSM, or using a KMS, the only way to access the key would be to gain physical access to the hardware where it is stored, or steal the KMS credentials and bypass all of its security measures.

## TLS configuration

This server has TLS configured to enable secure connections with HTTPS. This is done in 2 steps: generating a private key with a self-signed certificate, and creating an SSL context for the server to switch to using HTTPS instead of HTTP.

### Generating a key and a certificate

To enable TLS on the server a key and a certificate must be created.

The private key is generated using the RSA algorithm with a key size of 2048 bits - at the time of this writing this is the minimum recommended key size, which is sufficient for this example, but a higher size of 4096 bits is recommended to be used instead. Before writing the key to a file it is additionaly encrypted using an automatically selected algorithm considered to be the most suitable by the maintainers of the [cryptographic library used here](https://github.com/pyca/cryptography) (the Python Cryptographic Authority) and a randomly generated 256-bits-long passphrase.

A certificate which is required to enable TLS is then generated and signed by the private key. As the certificate is self-signed it has to be manually added to the list of trusted certificates which is an OS-dependant process.

For simplicity the private key and the certificate are stored locally, but in the same way as the data encryption key, these files contain sensitive data, and must be stored in a secure place, e.g. a physical/virtual HSM.

### Creating an SSL context

To enable HTTPS on the server an SSL context is created using the previously generated private key and certificate. This context is created using the default parameters which include but are not limited to:
* using the latest TLS version supported both by the client and the server - this is the only way to enable TLS v1.3 which is the late and most secure version of the protocol at the time of this writing
* forbidding SSLv2 and SSLv3 connections
* forbidding reuse of DH and ECDH keys
