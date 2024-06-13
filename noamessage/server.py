import socket
import threading
import sqlite3
from dbHandler import authenticate_user, create_tables, add_user, add_room, add_user_to_room, add_message, get_messages_for_room, get_groups_for_user

def handle_client(client_socket, addr):
    conn = sqlite3.connect('my.db')
    try:
        while True:
            request = client_socket.recv(4096).decode("utf-8")
            if request:
                command, *args = request.split(' ')
                if command == "LOGIN":
                    username, password = args
                    user_id = authenticate_user(conn, username, password)
                    if user_id:
                        response = f"Login successful {user_id}"
                    else:
                        response = "Invalid credentials"
                elif command == "REGISTER":
                    print("REGISTER command")
                    username, password = args
                    user_id = add_user(conn, (username, password))
                    response = f"User {username} registered with id {user_id}"
                elif command == "CREATE_GROUP":
                    print("CREATE_GROUP command")
                    group_name, user_id = args
                    room_id = add_room(conn, (group_name,))
                    add_user_to_room(conn, user_id, room_id)
                    response = f"Group {group_name} created with id {room_id}"
                elif command == "SEND_MESSAGE":
                    print("SEND_MESSAGE command")
                    group_id, user_id, message = args
                    message_id = add_message(conn, (message, None, user_id, group_id))
                    response = f"Message sent with id {message_id}"
                elif command == "FETCH_MESSAGES":
                    # print("FETCH_MESSAGES command")
                    # group_id = args[0]
                    # messages = get_messages_for_room(conn, group_id)
                    # # response = '\n'.join([f"{username}: {text} ({date})" for username, text, date in messages])
                    # if messages:
                    #     response = '\n'.join([f"{username}: {text} ({date})" for username, text, date in messages])
                    print("FETCH_MESSAGES command")
                    group_id = args[0]
                    messages = get_messages_for_room(conn, group_id)
                    if messages:
                        response = '\n'.join(
                            [f"{username}: {text} ({date})" if date else f"{username}: {text}" for username, text, date
                             in messages])
                    else:
                        response = "no messages for this room id"
                elif command == "GET_GROUPS":
                    print("GET_GROUPS command")
                    user_id = args[0]

                    groups = get_groups_for_user(conn, user_id)
                    if groups:
                        response = '\n'.join([f"{group_id} {group_name}" for group_id, group_name in groups])
                    else:
                        response = "You are not part of any groups."
                    # groups = get_groups_for_user(conn, user_id)
                    # response = '\n'.join([f"{group_id} {group_name}" for group_id, group_name in groups])
                else:
                    response = "Invalid command"

                print(response)
                client_socket.sendall(response.encode("utf-8"))

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
