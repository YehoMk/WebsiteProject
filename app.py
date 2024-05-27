from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = "1234"


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        print("|||Class0:|||", self.username)
        user_id_fetch = cursor.execute("""SELECT id FROM users WHERE username=(?)""", (self.username,)).fetchone()
        print("|||Class1:|||", user_id_fetch)
        user_id = str(user_id_fetch[0])
        print("|||Class2:|||", user_id)
        return user_id


@login_manager.user_loader
def load_user(user_id):
    if user_id is None or user_id == "None":
        user_id = -1

    print("User_loader user_id:", user_id)
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    username_fetch = cursor.execute("""SELECT username FROM users WHERE id=(?)""", (user_id,)).fetchone()
    print(username_fetch)
    username = username_fetch[0]
    print("User_loader username: ", username)
    password_fetch = cursor.execute("""SELECT password FROM users WHERE id=(?)""", (user_id,)).fetchone()
    password = password_fetch[0]
    print("User_loader password:", password)
    user = User(username, password)
    return user


def select_username_users():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    username_column_fetch = cursor.execute("""SELECT username FROM users""").fetchall()
    username_column = []
    for element in username_column_fetch:
        username_column.append(element[0])
    return username_column


def select_password_users():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    password_column_fetch = cursor.execute("""SELECT password FROM users""").fetchall()
    password_column = []
    for element in password_column_fetch:
        password_column.append(element[0])
    return password_column


def select_id_users():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    id_column_fetch = cursor.execute("""SELECT id FROM users""").fetchall()
    id_column = []
    for element in id_column_fetch:
        id_column_fetch.append(element[0])
    return id_column


def insert_users(username, password):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""
                   INSERT INTO users
                   (
                   username, password
                   )
                   VALUES
                   (?, ?)
                   """, (username, password))
    connection.commit()


@app.route("/", methods=["POST", "GET"])
@app.route("/index/", methods=["POST", "GET"])
@app.route("/home/", methods=["POST", "GET"])
def index():

    if request.method == "POST":

        username = request.form["username"]
        password_to_check = request.form["password"]

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        password = cursor.execute("""SELECT password FROM users WHERE username=(?)""", (username,)).fetchone()[0]

        print(username)
        print(password)
        user = User(username, password)

        if user:
            if bcrypt.check_password_hash(password, password_to_check):
                login_user(user)
                print(user.username, user.password, user)

    return render_template("index.html")


@app.route("/houses/")
def houses():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    houses_table = cursor.execute("""
                   SELECT * FROM houses ORDER BY id DESC
                   """).fetchall()

    connection.close()
    return render_template("houses.html", houses_table=houses_table)


@app.route("/sell/", methods=["POST", "GET"])
def sell():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        image = request.form["image"]
        location = request.form["location"]

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("""
                       INSERT INTO houses
                       (
                       name, description, price, image, location
                       )
                       VALUES
                       (?, ?, ?, ?, ?)
                       """, (name, description, price, image, location))
        connection.commit()
        connection.close()
        return redirect(url_for("sell"))
    return render_template("sell.html")


@app.route("/support/")
def support():
    return "Support"


@app.route("/about/")
def about():
    return "About"


@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"])

        print(select_username_users())
        if username not in select_username_users():
            insert_users(username, password)
            return redirect(url_for("index"))
        else:
            print("Error: repeating username")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
