import math
import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import torch
from torchvision.transforms import transforms
from facenet_pytorch import InceptionResnetV1, MTCNN, extract_face
import db
import psycopg2
import numpy as np
from ultralytics import YOLO
import subprocess
import sys

class AddFaceApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Add new Face")

        self.background_image = Image.open("D:\\Code\\DATN\\Images\\BG.jpg")
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(master, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

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

        self.label_username = ttk.Label(self.master, text="Username:")
        self.label_username.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="nsew")
        self.entry_username = ttk.Entry(self.master, width=30)
        self.entry_username.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")

        self.button_register_face = ttk.Button(self.master, text="Register", command=self.register_face)
        self.button_register_face.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="ew")

        self.button_exit = ttk.Button(self.master, text="Exit", command=self.exit)
        self.button_exit.grid(row=4, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="ew")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_rowconfigure(2, weight=0)
        self.master.grid_rowconfigure(3, weight=0)
        self.master.grid_rowconfigure(4, weight=0)
        self.master.grid_columnconfigure(0, weight=1)

    def exit(self):
        subprocess.Popen(["python", "main_screen.py"])
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

    def register_face(self):
        username = self.entry_username.get()

        check_username = "SELECT user_id FROM users WHERE username = %s"
        result = db.fetch_one(check_username, (username,))
        if result:
            success, frame = self.cap.read()

            if success:
                if self.is_real_face(frame):
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    boxes, _ = self.mtcnn.detect(rgb_frame)

                    if boxes is not None:
                        box = boxes[0]
                        face = extract_face(rgb_frame, box)
                        face_embedding = self.get_face_embedding(face)
                        if face_embedding is not None:
                            self.save_face_encoding(username, face_embedding)
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
    root.geometry("350x500")
    app = AddFaceApp(root)
    root.mainloop()