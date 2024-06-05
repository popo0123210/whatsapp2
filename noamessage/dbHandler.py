# def create table
# def signnewUser
# def check if user exists - for login
# def new group
# def add user to group
# def new message

import sqlite3


# def create_sqlite_database(filename):
#     """ create a database connection to an SQLite database """
#     conn = None
#     try:
#         conn = sqlite3.connect(filename)
#         print(sqlite3.sqlite_version)
#     except sqlite3.Error as e:
#         print(e)
#     finally:
#         if conn:
#             conn.close()


def create_tables():
    sql_statements = [
        """
        CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        username text NOT NULL,
        password text NOT NULL
        );""",
        """
        CREATE TABLE IF NOT EXISTS message (
          id INTEGER PRIMARY KEY,
          text text NOT NULL,
          date date,
          sender INT NOT NULL,
          room INT NOT NULL,
          FOREIGN KEY (sender) REFERENCES user (id),
          FOREIGN KEY (room) REFERENCES room (id)
        );""",
        """CREATE TABLE IF NOT EXISTS room (
          id INTEGER PRIMARY KEY,
          name text NOT NULL
        );""",
        """
        CREATE TABLE IF NOT EXISTS users_rooms (
          id INTEGER PRIMARY KEY,
          room_id INTEGER,
          user_id INTEGER,
          FOREIGN KEY (room_id) REFERENCES room (id),
          FOREIGN KEY (user_id) REFERENCES user (id)
        );"""
    ]

    # create a database connection
    try:
        with sqlite3.connect('my.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()
    except sqlite3.Error as e:
        print(e)


def add_user(conn, user):
    sql = ''' INSERT INTO user(username,password)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()

    return cur.lastrowid


def add_room(conn, room):
    sql = ''' INSERT INTO room(name)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, room)
    conn.commit()

    return cur.lastrowid

def add_message(conn, message):
    sql = '''INSERT INTO message(text,date,sender,room)
             VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, message)
    conn.commit()
    return cur.lastrowid

def add_message(conn, users_rooms):
    sql = '''INSERT INTO message(text,date,sender,room)
             VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, users_rooms)
    conn.commit()
    return cur.lastrowid

