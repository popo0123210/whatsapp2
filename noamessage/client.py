import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog


class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client")

        # Create a canvas widget and scrollbars
        self.canvas = tk.Canvas(master)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(master, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame inside the canvas
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)

        # Chat area
        self.chat_label = tk.Label(self.scrollable_frame, text="Chat:")
        self.chat_label.pack()

        self.chat_area = scrolledtext.ScrolledText(self.scrollable_frame, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Enter message
        self.msg_label = tk.Label(self.scrollable_frame, text="Enter message:")
        self.msg_label.pack()

        self.msg_entry = tk.Entry(self.scrollable_frame, width=50)
        self.msg_entry.pack(padx=20, pady=5)

        self.send_button = tk.Button(self.scrollable_frame, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        # Groups
        self.group_label = tk.Label(self.scrollable_frame, text="Groups:")
        self.group_label.pack()

        self.group_listbox = tk.Listbox(self.scrollable_frame)
        self.group_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.group_listbox.bind('<<ListboxSelect>>', self.on_group_select)

        self.create_group_button = tk.Button(self.scrollable_frame, text="Create Group", command=self.create_group)
        self.create_group_button.pack(pady=5)

        self.client_socket = None

        self.server_ip = "127.0.0.1"
        self.server_port = 8000

        self.current_group_id = None

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
        if response.startswith("Login successful"):
            self.user_id = response.split()[-1]  # Extract user ID from response
            self.login_window.destroy()
            self.fetch_groups()
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()
        else:
            messagebox.showerror("Login Failed", response)

    # def login(self):
    #     username = self.username_entry.get()
    #     password = self.password_entry.get()
    #     self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.client_socket.connect((self.server_ip, self.server_port))
    #     self.client_socket.send(f"LOGIN {username} {password}".encode('utf-8'))
    #     response = self.client_socket.recv(1024).decode('utf-8')
    #     if response == "Login successful":
    #         self.login_window.destroy()
    #         self.user_id = 1  # Replace with actual user ID from the server
    #         self.fetch_groups()
    #         self.receive_thread = threading.Thread(target=self.receive_messages)
    #         self.receive_thread.start()
    #     else:
    #         messagebox.showerror("Login Failed", response)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_ip, self.server_port))
        self.client_socket.send(f"REGISTER {username} {password}".encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')
        messagebox.showinfo("Register", response)

    def fetch_groups(self):
        self.client_socket.send(f"GET_GROUPS {self.user_id}".encode('utf-8'))
        groups = self.client_socket.recv(1024).decode('utf-8')
        self.group_listbox.delete(0, tk.END)
        for group in groups.split('\n'):
            self.group_listbox.insert(tk.END, group)

    def fetch_messages(self, group_id):
        print("fetch_messages")

        self.client_socket.send(f"FETCH_MESSAGES {group_id} {self.user_id}".encode('utf-8'))

        messages = ""
        print(messages)
        while True:
            chunk = self.client_socket.recv(1024).decode('utf-8')
            if chunk == "" or not chunk or chunk == "OVER":
                break
            print(chunk)

            messages += chunk

        print(messages)

        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, messages + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)
        # self.client_socket.send(f"FETCH_MESSAGES {group_id} {self.user_id}".encode('utf-8'))
        # messages = self.client_socket.recv(4096).decode('utf-8')
        # self.chat_area.config(state='normal')
        # self.chat_area.insert(tk.END, messages + "\n")
        # self.chat_area.config(state='disabled')
        # self.chat_area.yview(tk.END)

    def create_group(self):
        group_name = simpledialog.askstring("Create Group", "Enter group name:")
        if group_name:
            self.client_socket.send(f"CREATE_GROUP {group_name} {self.user_id}".encode('utf-8'))
            try:
                response = self.client_socket.recv(1024).decode('utf-8')
                if response.startswith("Group"):
                    group_id = response.split()[-1]
                    self.master.after(0, self.group_listbox.insert, tk.END, f"{group_name} (ID: {group_id})")
                else:
                    messagebox.showerror("Group Creation Failed", response)
            except Exception as e:
                messagebox.showerror("Error", f"Error creating group: {e}")

    # def fetch_groups(self):
    #     self.client_socket.send(f"GET_GROUPS {self.user_id}".encode('utf-8'))
    #     groups = self.client_socket.recv(1024).decode('utf-8')
    #     self.group_listbox.delete(0, tk.END)
    #     for group in groups.split('\n'):
    #         self.group_listbox.insert(tk.END, group)
    #
    # def fetch_messages(self, group_id):
    #     self.client_socket.send(f"FETCH_MESSAGES {group_id}".encode('utf-8'))
    #     messages = self.client_socket.recv(4096).decode('utf-8')
    #     self.chat_area.config(state='normal')
    #     self.chat_area.insert(tk.END, messages + "\n")
    #     self.chat_area.config(state='disabled')
    #     self.chat_area.yview(tk.END)

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
        if msg and self.current_group_id:
            self.client_socket.send(f"SEND_MESSAGE {self.current_group_id} {self.user_id} {msg}".encode("utf-8"))
            self.msg_entry.delete(0, tk.END)
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, f"You: {msg}\n")
            self.chat_area.config(state='disabled')
            self.chat_area.yview(tk.END)

    # def create_group(self):
    #     group_name = simpledialog.askstring("Create Group", "Enter group name:")
    #     if group_name:
    #         self.client_socket.send(f"CREATE_GROUP {group_name} {self.user_id}".encode('utf-8'))
    #         response = self.client_socket.recv(1024).decode('utf-8')
    #         group_id = response.split()[-1]
    #         self.group_listbox.insert(tk.END, f"{group_name} (ID: {group_id})")

    def on_group_select(self, event):
        selection = event.widget.curselection()
        if selection:
            group_info = event.widget.get(selection[0])
            group_id = group_info.split("ID: ")[-1][:-1]
            self.current_group_id = group_id
            self.chat_area.config(state='normal')
            self.chat_area.delete(1.0, tk.END)
            self.chat_area.config(state='disabled')
            self.fetch_messages(group_id)

    def on_closing(self):
        if self.client_socket:
            self.client_socket.close()
        self.master.quit()


def run_client():
    root = tk.Tk()
    root.geometry("600x400")  # Set initial size to 600x400 pixels
    root.resizable(width=True, height=True)  # Lock window size
    client = ChatClient(root)
    root.protocol("WM_DELETE_WINDOW", client.on_closing)
    root.mainloop()


run_client()
