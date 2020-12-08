from flask import Flask, render_template, request
import database
import exceptions
import data_encryption

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
    email, password, biography = data["email"], data["password"], data["biography"]

    try:
        database.set_biography(email, password, biography)
    except exceptions.InvalidCredentialsError:
        return "Invalid credentials"

    return "Set biography successfully"


@app.route("/users-list", methods=["GET"])
def users_list():
    users_list = database.get_users()
    return render_template("users_list.html", users_list=users_list)


if __name__ == "__main__":
    data_encryption.create_kek()
    database.drop()
    database.create()
    app.run(host="0.0.0.0")