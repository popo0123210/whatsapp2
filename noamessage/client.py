import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client")

        # חיבור לשרת
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(("localhost", 8000))
        except socket.error as e:
            messagebox.showerror("Connection Error", str(e))
            self.master.quit()
            return

        # סטאפ לגוי
        self.setup_gui()

        # רישום או כניסה ראשונית
        self.register_or_login()

        # תראד לקבלת הודעות כל הזמן שפןעלת התוכנה
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def setup_gui(self):
        self.master.geometry("800x600")
        self.master.configure(bg="#b0ec93")

        self.tab_control = ttk.Notebook(self.master)

        self.chat_frame = ttk.Frame(self.tab_control)
        self.groups_frame = ttk.Frame(self.tab_control)
        self.settings_frame = ttk.Frame(self.tab_control)
        self.contacts_frame = ttk.Frame(self.tab_control)

        self.tab_control.add(self.chat_frame, text="Chat")
        self.tab_control.add(self.groups_frame, text="Groups")
        self.tab_control.add(self.settings_frame, text="Settings")
        self.tab_control.add(self.contacts_frame, text="Contacts")
        self.tab_control.pack(expand=1, fill="both")

        # צאט
        self.chat_label = tk.Label(self.chat_frame, text="Chat:", bg="#b0ec93", fg="white", font=("Arial", 14))
        self.chat_label.pack()

        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, state='disabled', bg="#c4e5c8",
                                                   fg="white")
        self.chat_area.pack(padx=20, pady=5)

        self.msg_label = tk.Label(self.chat_frame, text="Enter message:", bg="#5fd36d", fg="white", font=("Arial", 12))
        self.msg_label.pack()

        self.msg_entry = tk.Entry(self.chat_frame, width=50, bg="#9ec6a3", fg="white")
        self.msg_entry.pack(padx=20, pady=5)

        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message, bg="#23b834", fg="white",
                                     font=("Arial", 12))
        self.send_button.pack(pady=5)

        # קבוצות
        self.group_label = tk.Label(self.groups_frame, text="Groups:", bg="#2b3e50", fg="white", font=("Arial", 14))
        self.group_label.pack()

        self.group_listbox = tk.Listbox(self.groups_frame, bg="#4a6a80", fg="white")
        self.group_listbox.pack(padx=20, pady=5)
        self.group_listbox.bind('<<ListboxSelect>>', self.on_group_select)

        self.create_group_button = tk.Button(self.groups_frame, text="Create Group", command=self.create_group,
                                             bg="#3b4f63", fg="white", font=("Arial", 12))
        self.create_group_button.pack(pady=5)

        self.join_group_button = tk.Button(self.groups_frame, text="Join Group", command=self.join_group, bg="#3b4f63",
                                           fg="white", font=("Arial", 12))
        self.join_group_button.pack(pady=5)

        self.add_user_button = tk.Button(self.groups_frame, text="Add User to Group", command=self.add_user_to_group,
                                         bg="#3b4f63", fg="white", font=("Arial", 12))
        self.add_user_button.pack(pady=5)

        self.group_info_button = tk.Button(self.groups_frame, text="Group Info", command=self.group_info, bg="#3b4f63",
                                           fg="white", font=("Arial", 12))
        self.group_info_button.pack(pady=5)

        # Settings frame
        self.settings_label = tk.Label(self.settings_frame, text="User Settings:", bg="#2b3e50", fg="white",
                                       font=("Arial", 14))
        self.settings_label.pack()

        self.username_label = tk.Label(self.settings_frame, text="Username:", bg="#2b3e50", fg="white",
                                       font=("Arial", 12))
        self.username_label.pack()
        self.username_entry = tk.Entry(self.settings_frame, width=30, bg="#4a6a80", fg="white")
        self.username_entry.pack(padx=20, pady=5)

        self.password_label = tk.Label(self.settings_frame, text="Password:", bg="#2b3e50", fg="white",
                                       font=("Arial", 12))
        self.password_label.pack()
        self.password_entry = tk.Entry(self.settings_frame, width=30, show='*', bg="#4a6a80", fg="white")
        self.password_entry.pack(padx=20, pady=5)

        self.update_button = tk.Button(self.settings_frame, text="Update", command=self.update_settings, bg="#3b4f63",
                                       fg="white", font=("Arial", 12))
        self.update_button.pack(pady=5)

        # Contacts frame
        self.contacts_label = tk.Label(self.contacts_frame, text="Contacts:", bg="#2b3e50", fg="white",
                                       font=("Arial", 14))
        self.contacts_label.pack()

        self.contact_listbox = tk.Listbox(self.contacts_frame, bg="#4a6a80", fg="white")
        self.contact_listbox.pack(padx=20, pady=5)

        self.add_contact_button = tk.Button(self.contacts_frame, text="Add Contact", command=self.add_contact,
                                            bg="#3b4f63", fg="white", font=("Arial", 12))
        self.add_contact_button.pack(pady=5)

        self.remove_contact_button = tk.Button(self.contacts_frame, text="Remove Contact", command=self.remove_contact,
                                               bg="#3b4f63", fg="white", font=("Arial", 12))
        self.remove_contact_button.pack(pady=5)

        self.current_group = None
        self.username = None
        self.user_id = None

    def register_or_login(self):
        action = simpledialog.askstring("Action", "Do you want to register or login? (register/login)")
        if action == "register":
            self.register()
        elif action == "login":
            self.login()
        else:
            messagebox.showerror("Error", "Invalid action")
            self.master.quit()

    def register(self):
        self.username = simpledialog.askstring("Username", "Enter your username")
        self.password = simpledialog.askstring("Password", "Enter your password", show='*')
        self.send_command(f"REGISTER {self.username} {self.password}")
        response = self.client_socket.recv(1024).decode("utf-8")
        messagebox.showinfo("Info", response)
        if "successful" in response:
            self.login()
        else:
            self.master.quit()

    def login(self):
        self.username = simpledialog.askstring("Username", "Enter your username")
        self.password = simpledialog.askstring("Password", "Enter your password", show='*')
        self.send_command(f"LOGIN {self.username} {self.password}")
        response = self.client_socket.recv(1024).decode("utf-8")
        if response.startswith("Login successful"):
            self.user_id = response.split()[2]
            self.fetch_groups()
            self.fetch_contacts()
        else:
            messagebox.showerror("Error", "Login failed")
            self.master.quit()

    def fetch_groups(self):
        self.send_command(f"GET_GROUPS {self.user_id}")
        response = self.client_socket.recv(1024).decode("utf-8")
        self.group_listbox.delete(0, tk.END)
        for group in response.split('\n'):
            if group:
                self.group_listbox.insert(tk.END, group)

    def fetch_contacts(self):
        self.send_command(f"GET_CONTACTS {self.user_id}")
        response = self.client_socket.recv(1024).decode("utf-8")
        self.contact_listbox.delete(0, tk.END)
        for contact in response.split('\n'):
            if contact:
                self.contact_listbox.insert(tk.END, contact)

    def on_group_select(self, event):
        selection = event.widget.curselection()
        if selection:
            self.current_group = event.widget.get(selection[0])
            self.fetch_messages()

    def fetch_messages(self):
        if self.current_group:
            group_id = self.current_group.split()[-1].strip("()")
            self.send_command(f"FETCH_MESSAGES {group_id}")
            response = self.client_socket.recv(1024).decode("utf-8")
            self.chat_area.config(state='normal')
            self.chat_area.delete(1.0, tk.END)
            self.chat_area.insert(tk.END, response)
            self.chat_area.config(state='disabled')

    def send_message(self):
        if self.current_group:
            group_id = self.current_group.split()[-1].strip("()")
            message = self.msg_entry.get()
            if message:
                self.send_command(f"SEND_MESSAGE {group_id} {self.user_id} {message}")
                self.msg_entry.delete(0, tk.END)
                self.fetch_messages()

    def send_command(self, command):
        try:
            self.client_socket.sendall(command.encode("utf-8"))
        except socket.error as e:
            messagebox.showerror("Error", str(e))
            self.master.quit()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                if message:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, message + "\n")
                    self.chat_area.yview(tk.END)
                    self.chat_area.config(state='disabled')
            except socket.error as e:
                messagebox.showerror("Error", str(e))
                break

    def create_group(self):
        group_name = simpledialog.askstring("Group Name", "Enter the group name")
        if group_name:
            self.send_command(f"CREATE_GROUP {group_name} {self.user_id}")
            response = self.client_socket.recv(1024).decode("utf-8")
            messagebox.showinfo("Info", response)
            self.fetch_groups()

    def join_group(self):
        group_name = simpledialog.askstring("Group Name", "Enter the group name to join")
        if group_name:
            self.send_command(f"JOIN_GROUP {group_name} {self.user_id}")
            response = self.client_socket.recv(1024).decode("utf-8")
            messagebox.showinfo("Info", response)
            self.fetch_groups()

    def add_user_to_group(self):
        if self.current_group:
            user_id = simpledialog.askstring("User ID", "Enter the user ID to add to the group")
            if user_id:
                group_id = self.current_group.split()[-1].strip("()")
                self.send_command(f"ADD_USER_TO_GROUP {group_id} {user_id}")
                response = self.client_socket.recv(1024).decode("utf-8")
                messagebox.showinfo("Info", response)

    def group_info(self):
        if self.current_group:
            group_id = self.current_group.split()[-1].strip("()")
            self.send_command(f"GROUP_INFO {group_id}")
            response = self.client_socket.recv(1024).decode("utf-8")
            messagebox.showinfo("Group Info", response)

    def update_settings(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            self.send_command(f"UPDATE_SETTINGS {self.user_id} {username} {password}")
            response = self.client_socket.recv(1024).decode("utf-8")
            messagebox.showinfo("Info", response)
            if "successful" in response:
                self.username = username

    def add_contact(self):
        contact_name = simpledialog.askstring("Contact Name", "Enter the contact name")
        if contact_name:
            self.send_command(f"ADD_CONTACT {self.user_id} {contact_name}")
            response = self.client_socket.recv(1024).decode("utf-8")
            messagebox.showinfo("Info", response)
            self.fetch_contacts()

    def remove_contact(self):
        selection = self.contact_listbox.curselection()
        if selection:
            contact_name = self.contact_listbox.get(selection[0])
            self.send_command(f"REMOVE_CONTACT {self.user_id} {contact_name}")
            response = self.client_socket.recv(1024).decode("utf-8")
            messagebox.showinfo("Info", response)
            self.fetch_contacts()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
