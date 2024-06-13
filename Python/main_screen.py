import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import sys

class MainScreen():
    def __init__(self, master):
        self.master = master
        self.master.title("Main Screen")

        self.background_image = Image.open("D:\\Code\\DATN\\Images\\ngoinha.png")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(master, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_widgets()

    def create_widgets(self):
        self.create_acc_button = tk.Button(self.master, text="Create Account", command=self.create_acc_button)
        self.create_acc_button.place(x=740, y=190, width=170, height=170)

        self.create_face_button = tk.Button(self.master, text="Create Face", command=self.create_face_button)
        self.create_face_button.place(x=740, y=451, width=170, height=170)

        self.device_button = tk.Button(self.master, text="Device", command=self.device_button)
        self.device_button.place(x=950, y=190, width=170, height=170)

    def create_acc_button(self):
        subprocess.Popen(["python", "Create_acc.py"])
        sys.exit()

    def create_face_button(self):
        subprocess.Popen(["python", "New_face.py"])
        sys.exit()

    def device_button(self):
        subprocess.Popen(["python", "Device.py"])
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1140x667+100+0")
    root.resizable(0, 0)
    app = MainScreen(root)
    root.mainloop()