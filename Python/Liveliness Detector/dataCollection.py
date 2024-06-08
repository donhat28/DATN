import cvzone
from cvzone.FaceDetectionModule import FaceDetector
import cv2
from time import time

classID = 0 # 0 - fake, 1 - real
outputFolder = "D:\Code\Face Recognition\Dataset\Fake"
confidence = 0.8
save = True
blurThreshold = 35

debug = False
offsetPercentageW = 10
offsetPercentageH = 20
camW, camH = 640, 480
floatingPoint = 6

cap = cv2.VideoCapture(0)
cap.set(3, camW)
cap.set(4, camH)
detector = FaceDetector()

while True:
    success, img = cap.read()
    imgOut = img.copy()
    img, bboxs = detector.findFaces(img, draw=False)

    listBlur = []
    listInfo = []

    if bboxs:
        #bboxs info (id, bbox, score, center)
        for bbox in bboxs:
            x, y, w, h = bbox["bbox"]
            score = float(bbox["score"][0])
            # print(score)
            # print(x, y, w, h)

            # Check the score
            if score > confidence:

                # Adding an offset to the face detected
                offsetW = (offsetPercentageW / 100) * w
                x = int(x - offsetW)
                w = int(w + offsetW * 2)

                offsetH = (offsetPercentageH / 100) * h
                y = int(y - offsetH * 3)
                h = int(h + offsetH * 3.5)

                # Avoid values below 0
                if x < 0: x = 0
                if y < 0: y = 0
                if w < 0: w = 0
                if h < 0: h = 0

                # Find blurriness
                imgFace = img[y:y + h, x:x + w]
                blurValue = int(cv2.Laplacian(imgFace, cv2.CV_64F).var())
                if blurValue > blurThreshold:
                    listBlur.append(True)
                else:
                    listBlur.append(False)

                # Normalize values
                ih, iw, _ = img.shape
                xc, yc = x + w / 2, y + h / 2
                # print(xc, yc)
                xcn, ycn = round(xc / iw, floatingPoint), round(yc / ih, floatingPoint)
                wn, hn = round(w / iw, floatingPoint), round(h / ih, floatingPoint)
                # print(xcn, ycn)
                # print(wn, hn)

                # Avoid values above 1
                if xcn > 1: xcn = 1
                if ycn > 1: ycn = 1
                if wn > 1: wn = 1
                if hn > 1: hn = 1

                listInfo.append(f"{classID} {xcn} {ycn} {wn} {hn}\n")

                # Draw
                cv2.rectangle(imgOut, (x, y, w, h), (255, 0, 255), 3)
                cvzone.putTextRect(imgOut, f"Score: {int(score * 100)}% Blur: {blurValue}",
                                   (x, y - 20), scale=2, thickness=3)

                if debug:
                    cv2.rectangle(img, (x, y, w, h), (255, 0, 255), 3)
                    cvzone.putTextRect(img, f"Score: {int(score * 100)}% Blur: {blurValue}",
                                       (x, y - 20), scale=2, thickness=3)

        # Save
        if save:
            if all(listBlur) and listBlur != []:
                # Save image
                timeNow = time()
                timeNow = str(timeNow).split('.')
                timeNow = timeNow[0] + timeNow[1]
                cv2.imwrite(f"{outputFolder}/{timeNow}.jpg", img)

                # Save Label text file
                for info in listInfo:
                    f = open(f"{outputFolder}/{timeNow}.txt", "a")
                    f.write(info)
                    f.close()

    cv2.imshow("Cam", imgOut)
    cv2.waitKey(1)