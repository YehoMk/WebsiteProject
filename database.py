import sqlite3


def houses_creation():

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""
                   CREATE TABLE houses 
                   (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   description TEXT NOT NULL,
                   price TEXT NOT NULL,
                   image TEXT NOT NULL,
                   location TEXT NOT NULL
                   )  
                   """)

    connection.commit()
    connection.close()


# houses_creation()


def houses_test(name, description, price, image, location):

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""
                   INSERT INTO houses
                   (name, description, price, image, location)
                   VALUES
                   (?, ?, ?, ?, ?)
                   """,
                   (name, description, price, image, location))
    connection.commit()
    connection.close()


# houses_test("Домівка", "Домівка в Києві.", "10000", "https://placehold.co/500x500", "Київ")
# houses_test("Квартира", "Квартира в Дніпрі.", "8000", "https://placehold.co/500x500", "Дніпрі")


def users_creation():

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""
                   CREATE TABLE users
                   (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT NOT NULL UNIQUE,
                   password TEXT NOT NULL 
                   )
                   """)
    connection.commit()
    connection.close()


houses_creation()
users_creation()
