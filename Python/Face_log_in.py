import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import face_recognition
import db
import numpy as np
from ultralytics import YOLO
import math

class FaceLogIn:
    def __init__(self, master):
        self.master = master
        self.master.title("Face Log-in")

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

        self.button_login = ttk.Button(self.master, text="Login", command=self.authenticate_face)
        self.button_login.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="ew")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=0)
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

    def authenticate_face(self):
        face_encodings = self.load_face_encodings_from_database()

        success, frame = self.cap.read()
        if success:
            if self.is_real_face(frame):
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_frame)
                if face_locations:
                    face_encodings_in_frame = face_recognition.face_encodings(rgb_frame, face_locations)

                    for face_encoding in face_encodings_in_frame:
                        for user_id, db_encoding in face_encodings.items():
                            match = face_recognition.compare_faces([db_encoding], face_encoding)
                            if match[0]:
                                self.log_login_attempt(user_id, True)
                                messagebox.showinfo("Success", "Login successful.")
                                return
                    self.log_login_attempt(None, False)
                    messagebox.showerror("Fail", "Login failed.")
                else:
                    messagebox.showerror("Error", "No face detected in the frame.")
            else:
                messagebox.showerror("Error", "Fake face detected.")

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

    def load_face_encodings_from_database(self):
        try:
            query = "SELECT user_id, face_encoding FROM face_encodings"
            results = db.fetch_all(query)

            face_encodings = {result[0]: np.frombuffer(result[1], dtype=np.float64) for result in results}

            return face_encodings
        except Exception as e:
            print(f"Error fetching face encodings from database: {e}")
            messagebox.showerror("Error", f"Error fetching face encodings from database: {e}")

    def log_login_attempt(self, user_id, success):
        try:
            query = "INSERT INTO login_attempts (user_id, success) VALUES (%s, %s)"
            db.execute_query(query, (user_id, success))
        except Exception as e:
            print(f"Error logging login attempt: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("720x530")
    app = FaceLogIn(root)
    root.mainloop()