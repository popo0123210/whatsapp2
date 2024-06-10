import sqlite3

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
          date DATE DEFAULT (datetime('now','localtime')),
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

def get_messages_for_room(conn, room_id):
    sql = '''SELECT u.username, m.text, m.date
             FROM message m
             JOIN user u ON m.sender = u.id
             WHERE m.room = ?
             ORDER BY m.date ASC'''
    cur = conn.cursor()
    cur.execute(sql, (room_id,))
    rows = cur.fetchall()
    return rows
