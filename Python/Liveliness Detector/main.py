import cvzone
from ultralytics import YOLO
import cv2
import math
import time
import torch

confidence = 0.8

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

if torch.cuda.is_available():
    device = torch.device('cuda')
else:
    device = torch.device('cpu')
print(device)

model = YOLO("Model/Liveliness_Detector.pt")
model.to(device)

classNames = ["Fake", "Real"]

prev_frame_time = 0
new_frame_time = 0

while True:
    new_frame_time = time.time()
    success, img = cap.read()
    img = cv2.flip(img, 1)

    results = model(img, stream=True, verbose=False)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            # Confidence
            conf = math.ceil((box.conf[0] * 100)) / 100

            # ClassNames
            cls = int(box.cls[0])
            if conf > confidence:
                if classNames[cls] == 'Real':
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)

                cvzone.cornerRect(img, (x1, y1, w, h), colorC=color, colorR=color)
                cvzone.putTextRect(img, f'{classNames[cls].upper()} {int(conf * 100)}%', (max(0, x1), max(35, y1)),
                                   scale=2, thickness=4, colorR=color, colorB=color)

    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    print(fps)

    cv2.imshow("Camera", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
