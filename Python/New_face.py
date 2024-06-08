import math
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import face_recognition
import db
import psycopg2
import numpy as np
from ultralytics import YOLO

class AddFaceApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Add new Face")

        self.cap = cv2.VideoCapture(0)
        self.model = YOLO("D:\Code\DATN\Python\Liveliness Detector\Model\Liveliness_Detector.pt")
        self.classNames = ["Fake", "Real"]

        self.create_widgets()
        self.show_video()

    def create_widgets(self):
        self.video_frame = ttk.Frame(self.master)
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.canvas = tk.Canvas(self.video_frame, width=600, height=400)
        self.canvas.pack()

        self.label_username = ttk.Label(self.master, text="Username:")
        self.label_username.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="nsew")
        self.entry_username = ttk.Entry(self.master, width=30)
        self.entry_username.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")

        self.button_register_face = ttk.Button(self.master, text="Register", command=self.register_face)
        self.button_register_face.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="ew")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_rowconfigure(2, weight=0)
        self.master.grid_rowconfigure(3, weight=0)
        self.master.grid_columnconfigure(0, weight=1)

    def show_video(self):
        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.imgtk = imgtk
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.master.after(10, self.show_video)

    def register_face(self):
        username = self.entry_username.get()

        check_username = "SELECT user_id FROM users WHERE username = %s"
        result = db.fetch_one(check_username, (username,))
        if result:
            success, frame = self.cap.read()

            if success:
                if self.is_real_face(frame):
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    face_locations = face_recognition.face_locations(rgb_frame)

                    if face_locations:
                        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                        if face_encodings:
                            face_encoding = face_encodings[0]
                            self.save_face_encoding(username, face_encoding)
                        else:
                            messagebox.showerror("Error","No face encoding found.")
                    else:
                        messagebox.showerror("Error", "No face detected.")
                else:
                    messagebox.showerror("Error", "Fake face detected.")
            else:
                messagebox.showerror("Error", "Failed to capture frame.")
        else:
            messagebox.showerror("Error", "Username not found.")

    def is_real_face(self, frame):
        results = self.model(frame, stream=False, verbose=False)
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                if conf > 0.8:
                    if self.classNames[cls] == 'Real':
                        return True
            return False

    def save_face_encoding(self, username, face_encoding):
        try:
            query_fetch_user_id = "SELECT user_id FROM users WHERE username = %s"
            user_id = db.fetch_one(query_fetch_user_id, (username,))

            if user_id:
                user_id = user_id[0]

                query_check_encoding = "SELECT encoding_id FROM face_encodings WHERE user_id = %s"
                existing_encoding = db.fetch_one(query_check_encoding, (user_id,))

                if existing_encoding:
                    query_update_encoding = "UPDATE face_encodings SET face_encoding = %s WHERE user_id = %s"
                    db.execute_query(query_update_encoding, (psycopg2.Binary(np.array(face_encoding)), user_id))
                    messagebox.showinfo("Success", "Face updated successfully.")
                else:
                    query_insert_encoding = "INSERT INTO face_encodings (user_id, face_encoding) VALUES (%s, %s)"
                    db.execute_query(query_insert_encoding, (user_id, psycopg2.Binary(np.array(face_encoding))))
                    messagebox.showinfo("Success", "Face encoding saved successfully.")
            else:
                messagebox.showerror("Error", "User not found.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("720x530")
    app = AddFaceApp(root)
    root.mainloop()