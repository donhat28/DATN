import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
import db

class CreateAccountApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Create New Account")

        self.create_widgets()

    def create_widgets(self):
        self.label_name = ttk.Label(self.master, text="Name:")
        self.label_name.grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = ttk.Entry(self.master)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        self.label_username = ttk.Label(self.master, text="Username:")
        self.label_username.grid(row=1, column=0, padx=5, pady=5)
        self.entry_username = ttk.Entry(self.master)
        self.entry_username.grid(row=1, column=1, padx=5, pady=5)

        self.label_password = ttk.Label(self.master, text="Password:")
        self.label_password.grid(row=2, column=0, padx=5, pady=5)
        self.entry_password = ttk.Entry(self.master, show="*")
        self.entry_password.grid(row=2, column=1, padx=5, pady=5)

        self.label_confirm_password = ttk.Label(self.master, text="Confirm Password:")
        self.label_confirm_password.grid(row=3, column=0, padx=5, pady=5)
        self.entry_confirm_password = ttk.Entry(self.master, show="*")
        self.entry_confirm_password.grid(row=3, column=1, padx=5, pady=5)

        self.button_create_user = ttk.Button(self.master, text="Create User", command=self.create_user)
        self.button_create_user.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def create_user(self):
        try:
            name = self.entry_name.get()
            username = self.entry_username.get()
            password = self.entry_password.get()
            confirm_password = self.entry_confirm_password.get()

            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match.")
                return

            password_hash = self.hash_password(password)

            check_username = "SELECT user_id FROM users WHERE username = %s"
            result = db.fetch_one(check_username, (username,))
            if result:
                messagebox.showerror("Error", "Username already exists.")
                return

            create_user = "INSERT INTO users (name, username, password_hash) VALUES (%s, %s, %s)"
            cursor = db.execute_query(create_user, (name, username, password_hash))

            if cursor:
                messagebox.showinfo("Success", "New user created successfully.")
            else:
                messagebox.showerror("Error", "An error occurred while creating the user.")

        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CreateAccountApp(root)
    root.mainloop()