import socket


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "127.0.0.1"
    server_port = 8000
    client.connect((server_ip, server_port))

    try:
        while True:
            # msg = input("Enter message: ")
            # in the server there will be commands, that will help you
            # determine what the action is and how to handle it
            new_user = '{"commandID": 2, "new_username": "username123", "password": "password123"}'
            msg = '{"id": 2, "name": "abc"}'
            client.send(msg.encode("utf-8")[:1024])

            response = client.recv(1024)
            response = response.decode("utf-8")

            if response.lower() == "closed":
                break

            print(f"Received: {response}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
        print("Connection to server closed")


run_client()
