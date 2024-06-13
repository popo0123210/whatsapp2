import socket
import threading
import sqlite3
from dbHandler import create_tables, add_user, add_room, add_message

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

def handle_client(client_socket, addr):
    conn = sqlite3.connect('my.db')
    try:
        while True:
            request = client_socket.recv(1024).decode("utf-8")
            if request:
                command, *args = request.split(' ')
                if command == "LOGIN":
                    print("login command recieved")
                    username, password = args
                    # Add authentication logic here
                    response = "Login successful"
                elif command == "REGISTER":
                    print("register command recieved")
                    username, password = args
                    user_id = add_user(conn, (username, password))
                    response = f"User {username} registered with id {user_id}"
                elif command == "CREATE_CHAT":
                    print("create chat command recieved")
                    chat_name = args[0]
                    room_id = add_room(conn, (chat_name,))
                    response = f"Chat {chat_name} created with id {room_id}"
                elif command == "SEND_MESSAGE":
                    print("send message command recieved")
                    chat_id, user_id, message = args
                    message_id = add_message(conn, (message, None, user_id, chat_id))
                    response = f"Message sent with id {message_id}"
                elif command == "FETCH_MESSAGES":
                    print(
                        "fetch messages command recieved"
                    )
                    chat_id = args[0]
                    messages = get_messages_for_room(conn, chat_id)
                    response = '\n'.join([f"{username}: {text} ({date})" for username, text, date in messages])
                else:
                    response = "Invalid command"

                client_socket.send(response.encode("utf-8"))

    except Exception as e:
        print(f"Error when handling client: {e}")
    finally:
        client_socket.close()
        print(f"Connection to client ({addr[0]}:{addr[1]}) closed")

def run_server():
    server_ip = "127.0.0.1"
    port = 8000

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((server_ip, port))
        server.listen()
        print(f"Listening on {server_ip}:{port}")

        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")

            thread = threading.Thread(target=handle_client, args=(client_socket, addr,))
            thread.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    create_tables()
    run_server()

