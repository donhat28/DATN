import torch
import torchvision
import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
from scipy.spatial.distance import cosine
import numpy as np

mtcnn = MTCNN(keep_all=True)

model = InceptionResnetV1(pretrained='vggface2').eval()

img = cv2.imread("WIN_20240610_10_24_28_Pro.jpg")
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
boxes, _ = mtcnn.detect(img_rgb)

face_embeddings = []

for box in boxes:
    x1, y1, x2, y2 = map(int, box)
    face = img_rgb[y1:y2, x1:x2]
    face = cv2.resize(face, (160, 160))
    face = torch.tensor(face).permute(2, 0, 1).float().unsqueeze(0)
    face_embedding = model(face)
    face_embeddings.append(face_embedding.detach().numpy())

print(face_embeddings)

# def is_match(known_embedding, candidate_embedding, threshold=0.5):
#     score = cosine(known_embedding, candidate_embedding)
#     return score <= threshold
#
# known_embedding = face_embeddings[0][0]
# candidate_embedding = face_embeddings[1][0]
# match = is_match(known_embedding, candidate_embedding)
# print("Khuôn mặt giống nhau" if match else "Khuôn mặt khác nhau")
