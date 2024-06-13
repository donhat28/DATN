import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import bcrypt
import db
import subprocess
import sys

class AccountLogIn:
    def __init__(self, master):
        self.master = master
        self.master.title("Log-in")

        self.background_image = Image.open("D:\\Code\\DATN\\Images\\BG.jpg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(master, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_widgets()

    def create_widgets(self):
        self.username_label = tk.Label(self.master, text="Username:")
        self.username_label.grid(row=0, column=0, padx=20, pady=20)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.grid(row=0, column=1, padx=20, pady=20)

        self.password_label = tk.Label(self.master, text="Password:")
        self.password_label.grid(row=1, column=0, padx=20, pady=20)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.grid(row=1, column=1, padx=20, pady=20)

        self.login_button = tk.Button(self.master, text="Login", command=self.login_clicked)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="ew")

        self.button_face_login = tk.Button(self.master, text="Face Login", command=self.open_face_login)
        self.button_face_login.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="ew")

    def open_face_login(self):
        subprocess.Popen(["python", "Face_log_in.py"])
        sys.exit()

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def authenticate(self, username, password):
        try:
            check_user = "SELECT user_id, password_hash FROM users WHERE username = %s"
            user_data = db.fetch_one(check_user, (username,))

            if user_data is not None:
                user_id, stored_password_hash = user_data
                if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                    # tk.messagebox.showinfo("Login", "Login successful!")
                    success = True
                    subprocess.Popen(["python", "main_screen.py"])
                    sys.exit()
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
    root.geometry("270x300")
    app = AccountLogIn(root)
    root.mainloop()

