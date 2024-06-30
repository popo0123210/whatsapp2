import socket
import threading
import sqlite3
import logging
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

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
clients = []

def handle_client(client_socket, addr):
    conn = sqlite3.connect('my.db')
    try:
        while True:
            request = client_socket.recv(1024).decode("utf-8")
            if request:
                logging.debug(f"Received request: {request}")
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
                    user_id, group_name = args
                    logging.debug(f"Creating group: {group_name} for user: {user_id}")
                    room_id = get_room_id_by_name(conn, group_name)
                    if room_id is None:
                        add_room(conn, (group_name,))
                        room_id = get_room_id_by_name(conn, group_name)
                        add_user_to_room(conn, user_id, room_id)
                        client_socket.send("Group created successfully!".encode("utf-8"))
                        logging.debug(f"Group created: {group_name} with ID: {room_id}")
                    else:
                        client_socket.send("Group already exists".encode("utf-8"))
                        logging.debug(f"Group already exists: {group_name}")
                elif command == "JOIN_GROUP":
                    user_id, group_name = args
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
                    user_id, group_id, *msg = args
                    msg = " ".join(msg)
                    add_message(conn, (msg, user_id, group_id))
                    broadcast_message(group_id, user_id, msg)
                elif command == "GET_MESSAGES":
                    group_id = args[0]
                    messages = get_messages_for_room(conn, group_id)
                    if messages:
                        response = "\n".join([f"{msg[0]}: {msg[1]}" for msg in messages])
                    else:
                        response = "No messages found"
                    client_socket.send(response.encode("utf-8"))
                else:
                    client_socket.send(f"Unknown command: {command}".encode("utf-8"))
            else:
                break
    except Exception as e:
        logging.error(f"Exception: {e}")
        client_socket.send(f"Error: {str(e)}".encode("utf-8"))
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
        try:
            client.send(formatted_message.encode("utf-8"))
        except Exception as e:
            logging.error(f"Error sending message to client: {e}")
    conn.close()

def run_server():
    create_tables()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8000))
    server.listen(5)
    logging.info("Server listening on port 8000")

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        logging.info(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

run_server()
