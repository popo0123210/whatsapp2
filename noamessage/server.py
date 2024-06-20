import socket
import threading
import sqlite3
from dbHandler import (
    create_tables,
    add_user,
    add_room,
    add_user_to_room,
    add_message,
    get_messages_for_room,
    get_groups_for_user,
    get_room_id_by_name,
    get_user_id_by_username,
)

clients = []

def handle_client(client_socket, addr):
    conn = sqlite3.connect('my.db')
    try:
        while True:
            request = client_socket.recv(1024).decode("utf-8")
            if request:
                print(f"Received request: {request}")
                command, *args = request.split()
                if command == "REGISTER":
                    username, password = args
                    user_id = get_user_id_by_username(conn, username)
                    if user_id is None:
                        add_user(conn, (username, password))
                        client_socket.send("Registration successful".encode("utf-8"))
                    else:
                        client_socket.send("Username already exists".encode("utf-8"))
                elif command == "LOGIN":
                    username, password = args
                    user_id = get_user_id_by_username(conn, username)
                    if user_id:
                        cur = conn.cursor()
                        cur.execute("SELECT password FROM user WHERE username = ?", (username,))
                        stored_password = cur.fetchone()[0]
                        if stored_password == password:
                            client_socket.send(f"Login successful {user_id}".encode("utf-8"))
                        else:
                            client_socket.send("Login failed".encode("utf-8"))
                    else:
                        client_socket.send("Login failed".encode("utf-8"))
                elif command == "GET_GROUPS":
                    user_id = args[0]
                    groups = get_groups_for_user(conn, user_id)
                    response = "\n".join([f"{group[1]} (ID: {group[0]})" for group in groups])
                    client_socket.send(response.encode("utf-8"))
                elif command == "CREATE_GROUP":
                    group_name, user_id = args
                    add_room(conn, (group_name,))
                    room_id = get_room_id_by_name(conn, group_name)
                    add_user_to_room(conn, user_id, room_id)
                    client_socket.send(f"Group {group_name} created with ID {room_id}".encode("utf-8"))
                elif command == "JOIN_GROUP":
                    group_name, user_id = args
                    room_id = get_room_id_by_name(conn, group_name)
                    if room_id:
                        add_user_to_room(conn, user_id, room_id)
                        client_socket.send(f"Joined group {group_name}".encode("utf-8"))
                    else:
                        client_socket.send(f"Group {group_name} not found".encode("utf-8"))
                elif command == "ADD_USER_TO_GROUP":
                    group_id, username = args
                    user_id = get_user_id_by_username(conn, username)
                    if user_id:
                        add_user_to_room(conn, user_id, group_id)
                        client_socket.send(f"User {username} added to group".encode("utf-8"))
                    else:
                        client_socket.send(f"User {username} not found".encode("utf-8"))
                elif command == "SEND_MESSAGE":
                    group_id, user_id, *msg = args
                    msg = " ".join(msg)
                    add_message(conn, (msg, user_id, group_id))
                    client_socket.send("Message sent".encode("utf-8"))
                    broadcast_message(group_id, user_id, msg)
                elif command == "FETCH_MESSAGES":
                    group_id = args[0]
                    messages = get_messages_for_room(conn, group_id)
                    response = "\n".join([f"{msg[0]}: {msg[1]}" for msg in messages])
                    client_socket.send(response.encode("utf-8"))
                else:
                    client_socket.send(f"Unknown command: {command}".encode("utf-8"))
            else:
                break
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        client_socket.close()
        conn.close()

def broadcast_message(group_id, user_id, message):
    conn = sqlite3.connect('my.db')
    cur = conn.cursor()
    cur.execute("SELECT username FROM user WHERE id = ?", (user_id,))
    username = cur.fetchone()[0]
    formatted_message = f"{username}: {message}"
    for client in clients:
        client.send(formatted_message.encode("utf-8"))
    conn.close()

def run_server():
    create_tables()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8000))
    server.listen(5)
    print("Server listening on port 8000")

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

run_server()
