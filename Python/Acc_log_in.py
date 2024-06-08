import tkinter as tk
from tkinter import messagebox
import bcrypt
import db

class AccountLogIn:
    def __init__(self, master):
        self.master = master
        self.master.title("Log-in")

        self.create_widgets()

    def create_widgets(self):
        self.username_label = tk.Label(self.master, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.master, text="Password:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self.master, text="Login", command=self.login_clicked)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def authenticate(self, username, password):
        try:
            check_user = "SELECT user_id, password_hash FROM users WHERE username = %s"
            user_data = db.fetch_one(check_user, (username,))

            if user_data is not None:
                user_id, stored_password_hash = user_data
                if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                    tk.messagebox.showinfo("Login", "Login successful!")
                    success = True
                else:
                    tk.messagebox.showerror("Login", "Incorrect password.")
                    success = False
            else:
                tk.messagebox.showerror("Login", "User not found.")
                user_id = None
                success = False

            db.execute_query(
                "INSERT INTO login_attempts (user_id, success) VALUES (%s, %s);",
                (user_id, success)
            )

        except Exception as e:
            tk.messagebox.showerror("Error", str(e))

    def login_clicked(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.authenticate(username, password)

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountLogIn(root)
    root.mainloop()

