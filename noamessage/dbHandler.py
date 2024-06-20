import sqlite3

def create_tables():
    sql_statements = [
        """
        CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
        );""",
        """
        CREATE TABLE IF NOT EXISTS message (
          id INTEGER PRIMARY KEY,
          text TEXT NOT NULL,
          date DATETIME DEFAULT CURRENT_TIMESTAMP,
          sender INTEGER NOT NULL,
          room INTEGER NOT NULL,
          FOREIGN KEY (sender) REFERENCES user (id),
          FOREIGN KEY (room) REFERENCES room (id)
        );""",
        """CREATE TABLE IF NOT EXISTS room (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL
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
    sql = ''' INSERT INTO user(username, password)
              VALUES(?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid

def add_room(conn, room):
    sql = ''' INSERT INTO room(name)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, room)
    conn.commit()
    return cur.lastrowid

def add_user_to_room(conn, user_id, room_id):
    sql = ''' INSERT INTO users_rooms(user_id, room_id)
              VALUES(?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (user_id, room_id))
    conn.commit()

def add_message(conn, message):
    sql = '''INSERT INTO message(text, date, sender, room)
             VALUES(?, CURRENT_TIMESTAMP, ?, ?) '''
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

def get_groups_for_user(conn, user_id):
    sql = '''SELECT r.id, r.name 
             FROM room r
             JOIN users_rooms ur ON ur.room_id = r.id
             WHERE ur.user_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (user_id,))
    rows = cur.fetchall()
    return rows

def get_user_id_by_username(conn, username):
    sql = '''SELECT id FROM user WHERE username = ?'''
    cur = conn.cursor()
    cur.execute(sql, (username,))
    row = cur.fetchone()
    return row[0] if row else None

def get_room_id_by_name(conn, name):
    sql = '''SELECT id FROM room WHERE name = ?'''
    cur = conn.cursor()
    cur.execute(sql, (name,))
    row = cur.fetchone()
    return row[0] if row else None
