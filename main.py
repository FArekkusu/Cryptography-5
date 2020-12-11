from flask import Flask, render_template, request
import ssl
import database
import exceptions
import data_encryption
import tls_config

app = Flask(__name__)


@app.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email, password = data["email"], data["password"]

    try:
        database.register(email, password)
    except exceptions.PasswordTooShortError:
        return "Password is too short"
    except exceptions.EmailMatchesPasswordError:
        return "Email address cannot be used as password"
    
    return "Activation link sent to the provided email address"


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email, password = data["email"], data["password"]

    try:
        database.login(email, password)
    except exceptions.InvalidCredentialsError:
        return "Invalid credentials"
    except exceptions.OutdatedPasswordVersionError:
        return "Please, reset your password"

    return "Logged in successfully"


@app.route("/biography", methods=["POST"])
def biography():
    data = request.get_json()
    email, password, biography_ = data["email"], data["password"], data["biography"]

    try:
        database.set_biography(email, password, biography_)
    except exceptions.InvalidCredentialsError:
        return "Invalid credentials"

    return "Set biography successfully"


@app.route("/users-list", methods=["GET"])
def users_list():
    users_list = database.get_users()
    return render_template("users_list.html", users_list=users_list)


if __name__ == "__main__":
    tls_config.create_key_cert_pair()
    data_encryption.create_kek()
    database.drop()
    database.create()

    with open(tls_config.PASSPHRASE_PATH, "rb") as f:
        passphrase = f.read()

    context = ssl.SSLContext()
    context.load_cert_chain(tls_config.CERT_PATH, tls_config.KEY_PATH, passphrase)

    app.run(host="0.0.0.0", ssl_context=context)