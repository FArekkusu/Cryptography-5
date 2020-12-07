from flask import Flask, render_template, request
import database
import exceptions

app = Flask(__name__, template_folder="")

@app.route("/")
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
    
    return "Activation link sent to the provided email address"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email, password = data["email"], data["password"]

    try:
        database.login(email, password)
    except exceptions.InvalidCredentialsError:
        return "Invalid credentials"

    return "Logged in successfully"

if __name__ == "__main__":
    database.create()
    app.run(host="0.0.0.0")