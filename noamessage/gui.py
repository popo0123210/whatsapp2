import tkinter as tk
from tkinter import messagebox, scrolledtext


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.username_label = tk.Label(self.frame, text="Username:")
        self.username_label.grid(row=0, column=0, pady=5)
        self.username_entry = tk.Entry(self.frame)
        self.username_entry.grid(row=0, column=1, pady=5)

        self.password_label = tk.Label(self.frame, text="Password:")
        self.password_label.grid(row=1, column=0, pady=5)
        self.password_entry = tk.Entry(self.frame, show='*')
        self.password_entry.grid(row=1, column=1, pady=5)

        self.login_button = tk.Button(self.frame, text="Login", command=self.check_credentials)
        self.login_button.grid(row=2, columnspan=2, pady=10)

    def check_credentials(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "user" and password == "pass":
            self.open_chat_window()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_chat_window(self):
        self.root.destroy()
        root = tk.Tk()
        ChatWindow(root)
        root.mainloop()


class ChatWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat")

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.groups_frame = tk.Frame(self.frame)
        self.groups_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.groups_label = tk.Label(self.groups_frame, text="Groups")
        self.groups_label.pack()

        self.groups_listbox = tk.Listbox(self.groups_frame)
        self.groups_listbox.pack(fill='both', expand=True)
        self.groups_listbox.bind('<<ListboxSelect>>', self.display_group_messages)

        self.chat_frame = tk.Frame(self.frame)
        self.chat_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.group_title = tk.Label(self.chat_frame, text="Select a group", font=("Arial", 16))
        self.group_title.pack(pady=5)

        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, state='disabled', width=50, height=20)
        self.chat_display.pack(pady=5)

        self.message_entry = tk.Entry(self.chat_frame, width=40)
        self.message_entry.pack(side='left', pady=5, padx=5, fill='x', expand=True)
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(side='right', pady=5, padx=5)

        self.populate_groups()

    def populate_groups(self):
        # Simulate group data fetching from a server
        self.groups = ["Group 1", "Group 2", "Group 3"]

        for group in self.groups:
            self.groups_listbox.insert(tk.END, group)

    def display_group_messages(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            group_name = event.widget.get(index)
            self.group_title.config(text=group_name)

            # Simulate fetching messages for the selected group from a server
            messages = self.fetch_group_messages(group_name)

            self.chat_display.config(state='normal')
            self.chat_display.delete(1.0, tk.END)
            for message in messages:
                self.chat_display.insert(tk.END, message + "\n")
            self.chat_display.config(state='disabled')
            self.chat_display.yview(tk.END)

    def fetch_group_messages(self, group_name):
        # Simulate fetching messages
        return [f"{group_name} - Message 1", f"{group_name} - Message 2", f"{group_name} - Message 3"]

    def send_message(self):
        message = self.message_entry.get()
        if message:
            current_group = self.group_title.cget("text")
            if current_group and current_group != "Select a group":
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, f"You: {message}\n")
                self.chat_display.config(state='disabled')
                self.chat_display.yview(tk.END)
                self.message_entry.delete(0, tk.END)
                # Here, you would also send the message to the server or other users


def main():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()

