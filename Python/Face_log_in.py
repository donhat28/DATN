import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import torch
from torchvision.transforms import transforms
from facenet_pytorch import InceptionResnetV1, MTCNN
import db
import numpy as np
from ultralytics import YOLO
import math
import subprocess
import sys

class FaceLogIn:
    def __init__(self, master):
        self.master = master
        self.master.title("Face Log-in")

        self.cap = cv2.VideoCapture(0)
        self.model = YOLO("D:\Code\DATN\Python\Liveliness Detector\Model\Liveliness_Detector.pt")
        self.classNames = ["Fake", "Real"]

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.mtcnn = MTCNN(keep_all=True, device=self.device)

        self.create_widgets()
        self.show_video()

    def create_widgets(self):
        self.video_frame = ttk.Frame(self.master)
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.canvas = tk.Canvas(self.video_frame, width=300, height=400)
        self.canvas.grid(row=0, column=0, padx=0, pady=0)

        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)

        self.button_login = ttk.Button(self.master, text="Login", command=self.login)
        self.button_login.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="ew")

        self.button_acc_login = ttk.Button(self.master, text="Account Login", command=self.open_account_login)
        self.button_acc_login.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_rowconfigure(2, weight=0)
        self.master.grid_columnconfigure(0, weight=1)

    def open_account_login(self):
        subprocess.Popen(["python", "Acc_log_in.py"])
        sys.exit()

    def show_video(self):
        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape

        center_x, center_y = frame_width // 2, frame_height // 2

        crop_width, crop_height = 300, 400
        half_crop_width, half_crop_height = crop_width // 2, crop_height // 2
        x1 = max(center_x - half_crop_width, 0)
        y1 = max(center_y - half_crop_height, 0)
        x2 = min(center_x + half_crop_width, frame_width)
        y2 = min(center_y + half_crop_height, frame_height)
        cropped_frame = frame[y1:y2, x1:x2]
        resized_frame = cv2.resize(cropped_frame, (300, 400))

        cv2image = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)

        imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.imgtk = imgtk
        self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.master.after(10, self.show_video)

    def login(self):
        try:
            success, frame = self.cap.read()
            if success:
                if self.is_real_face(frame):
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    boxes, _ = self.mtcnn.detect(rgb_frame)

                    if boxes is not None:
                        box = boxes[0]
                        face = self.extract_face(rgb_frame, box)
                        face_embedding = self.get_face_embedding(face)

                        if face_embedding is not None:
                            user_id = self.match_face_to_database(face_embedding)
                            if user_id:
                                username = self.get_username_from_user_id(user_id)
                                self.record_login_attempt(user_id, True)
                                messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                            else:
                                self.record_login_attempt(None, False)
                                messagebox.showerror("Login Failed", "Face not recognized.")
                        else:
                            self.record_login_attempt(None, False)
                            messagebox.showerror("Error", "No face encoding found.")
                    else:
                        self.record_login_attempt(None, False)
                        messagebox.showerror("Error", "No face detected.")
                else:
                    self.record_login_attempt(None, False)
                    messagebox.showerror("Error", "Fake face detected")
            else:
                self.record_login_attempt(None, False)
                messagebox.showerror("Error", "Failed to capture frame.")
        except Exception as e:
            self.record_login_attempt(None, False)
            messagebox.showerror("Error", f"An error occurred: {e}")

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

    def extract_face(self, frame, box):
        x1, y1, x2, y2 = box
        face = frame[int(y1):int(y2), int(x1):int(x2)]
        face = torch.from_numpy(face).permute(2, 0, 1).float().to(self.device)
        return face

    def get_face_embedding(self, face):
        if face is None:
            return None

        face_np = face.cpu().numpy()
        face_np = np.transpose(face_np, (1, 2, 0))
        face_np = (face_np * 255).astype(np.uint8)

        face_img = Image.fromarray(face_np)
        face_img = transforms.Resize((160, 160))(face_img)
        face_img = transforms.ToTensor()(face_img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            embedding = self.resnet(face_img)

        return embedding.cpu().numpy()

    def match_face_to_database(self, face_embedding):
        query_get_all_encodings = "SELECT * FROM face_encodings"
        encodings = db.fetch_all(query_get_all_encodings)

        for encoding in encodings:
            db_encoding = np.frombuffer(encoding[2], dtype=np.float32)
            distance = np.linalg.norm(db_encoding - face_embedding)
            if distance < 1.0:  # Adjust threshold as needed
                return encoding[1]

        return None

    def get_username_from_user_id(self, user_id):
        query_get_username = "SELECT username FROM users WHERE user_id = %s"
        username = db.fetch_one(query_get_username, (user_id,))
        return username[0] if username else None

    def record_login_attempt(self, user_id, success):
        try:
            query_insert_attempt = "INSERT INTO login_attempts (user_id, success) VALUES (%s, %s)"
            db.execute_query(query_insert_attempt, (user_id, success))
        except Exception as e:
            print(f"Error recording login attempt: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("350x500")
    app = FaceLogIn(root)
    root.mainloop()