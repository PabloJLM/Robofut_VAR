import cv2
import pickle
import os
import numpy as np


calibration_file = "calibration_data/calibration_matrices.p"
if not os.path.exists(calibration_file):
    print(f"Error: No se encontró {calibration_file}. Primero calibra la cámara.")
    exit()

with open(calibration_file, "rb") as f:
    calib_data = pickle.load(f)
    mtx = calib_data["mtx"]
    dist = calib_data["dist"]


link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.20:554/stream1" #blur =5 si es stream2 blur =9 si es stream1
cap = cv2.VideoCapture(link)

if not cap.isOpened():
    print("Error al abrir la transmisión RTSP")
    exit()

# Crear detector de blobs
params = cv2.SimpleBlobDetector_Params()
params.filterByColor = False  
params.filterByArea = True
params.minArea = 100
params.maxArea = 5000
params.filterByConvexity = True
params.minConvexity = 0.85
params.filterByCircularity = True
params.minCircularity = 0.7  
params.filterByInertia = False

detector = cv2.SimpleBlobDetector_create(params)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al recibir el frame")
        break

    corrected = cv2.undistort(frame, mtx, dist, None, mtx)
    
    hsv = cv2.cvtColor(corrected, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 150])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 150])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.medianBlur(mask, 9)

    keypoints = detector.detect(mask)

    result = corrected.copy()
    result = cv2.drawKeypoints(result, keypoints, None, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    #cv2.imshow("Original", corrected)
    cv2.imshow("Mascara Roja", mask)
    cv2.imshow("Detección de LED Rojo", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
