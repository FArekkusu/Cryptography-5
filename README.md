# Cryptography-5-6

This repository includes a simple server application showcasing:
* secure user registration and login;
* secure data storage.

Flask web framework is used as the basis for the server, for serving HTML pages, and processing the requests. All the logic is implemented manually.

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

TODO
