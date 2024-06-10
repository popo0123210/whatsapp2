import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client")

        self.chat_label = tk.Label(master, text="Chat:")
        self.chat_label.pack()

        self.chat_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(padx=20, pady=5)

        self.msg_label = tk.Label(master, text="Enter message:")
        self.msg_label.pack()

        self.msg_entry = tk.Entry(master, width=50)
        self.msg_entry.pack(padx=20, pady=5)

        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.client_socket = None

        self.server_ip = "127.0.0.1"
        self.server_port = 8000

        self.login_screen()

    def login_screen(self):
        self.login_window = tk.Toplevel(self.master)
        self.login_window.title("Login")

        self.username_label = tk.Label(self.login_window, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.pack()

        self.password_label = tk.Label(self.login_window, text="Password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.login_window, show='*')
        self.password_entry.pack()

        self.login_button = tk.Button(self.login_window, text="Login", command=self.login)
        self.login_button.pack()

        self.register_button = tk.Button(self.login_window, text="Register", command=self.register)
        self.register_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))
        self.client_socket.send(f"LOGIN {username} {password}".encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        if response == "Login successful":
            self.login_window.destroy()
            self.fetch_messages("1")  # Assuming chat_id = 1 for simplicity
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        else:
            messagebox.showerror("Login Failed", response)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))
        self.client_socket.send(f"REGISTER {username} {password}".encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        messagebox.showinfo("Register", response)

    def fetch_messages(self, chat_id):
        self.client_socket.send(f"FETCH_MESSAGES {chat_id}".encode('utf-8'))
        messages = self.client_socket.recv(4096).decode('utf-8')
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, messages + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def receive_messages(self):
        while True:
            try:
                response = self.client_socket.recv(1024).decode("utf-8")
                if response.lower() == "closed":
                    self.client_socket.close()
                    break
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, f"Server: {response}\n")
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Error receiving message: {e}")
                break

    def send_message(self):
        msg = self.msg_entry.get()
        if msg:
            self.client_socket.send(f"SEND_MESSAGE 1 1 {msg}".encode("utf-8"))
            self.msg_entry.delete(0, tk.END)
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, f"You: {msg}\n")
            self.chat_area.config(state='disabled')
            self.chat_area.yview(tk.END)

    def on_closing(self):
        if self.client_socket:
            self.client_socket.close()
        self.master.quit()

def run_client():
    root = tk.Tk()
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.on_closing)
    root.mainloop()

run_client()

