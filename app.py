from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = "1234"

app.config["UPLOAD_FOLDER"] = "upload"
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png"}


if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


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


def login():
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


@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/", methods=["POST", "GET"])
@app.route("/index/", methods=["POST", "GET"])
@app.route("/home/", methods=["POST", "GET"])
def index():

    login()

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    houses_table = cursor.execute("""SELECT * FROM houses ORDER BY id DESC""").fetchall()

    if len(houses_table) >= 3:
        index_offer_1 = houses_table[0]
        index_offer_2 = houses_table[1]
        index_offer_3 = houses_table[2]
    else:
        index_offer_1 = (0, "default", "default", "default", "https://placehold.co/200x200", "default", "default", "default", "default")
        index_offer_2 = (0, "default", "default", "default", "https://placehold.co/200x200", "default", "default", "default","default")
        index_offer_3 = (0, "default", "default", "default", "https://placehold.co/200x200", "default", "default", "default", "default")

    return render_template("index.html", index_offer_1=index_offer_1, index_offer_2=index_offer_2, index_offer_3=index_offer_3)


@app.route("/houses/", methods=["POST", "GET"])
def houses():

    login()

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    houses_table = cursor.execute("""
                   SELECT * FROM houses ORDER BY id DESC
                   """).fetchall()

    connection.close()
    return render_template("houses.html", houses_table=houses_table)


@app.route("/buy/<int:houses_id>", methods=["POST", "GET"])
def buy(houses_id):

    login()

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    houses_table = cursor.execute("""SELECT * FROM houses WHERE id=(?)""", (houses_id,)).fetchone()
    return render_template("buy.html", houses_table=houses_table)


@app.route("/sell/", methods=["POST", "GET"])
def sell():

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        preview_image = request.files["preview_image"]
        preview_image_filename = secure_filename(preview_image.filename)
        location = request.form["location"]
        offer_type = request.form["offer_type"]
        image = request.files["image"]
        image_filename = secure_filename(image.filename)
        user = current_user.username

        preview_image.save(os.path.join(app.config["UPLOAD_FOLDER"], preview_image_filename))
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("""
                       INSERT INTO houses
                       (
                       name, description, price, preview_image, location, offer_type, image, user
                       )
                       VALUES
                       (?, ?, ?, ?, ?, ?, ?, ?)
                       """, (name, description, price, preview_image_filename, location, offer_type, image_filename, user))
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

        if request.form["password"] == request.form["confirm_password"]:

            password = bcrypt.generate_password_hash(request.form["password"])

            print(select_username_users())
            if username not in select_username_users():
                insert_users(username, password)
                return redirect(url_for("index"))
            else:
                print("Error: repeating username")
                return redirect(url_for("signup"))
        else:
            pass

    return render_template("signup.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
