import cv2
import pickle
import os
import numpy as np

# Cargar calibración de la cámara
calibration_file = "calibration_data/calibration_matrices.p"
if not os.path.exists(calibration_file):
    print(f"Error: No se encontró {calibration_file}. Primero calibra la cámara.")
    exit()

with open(calibration_file, "rb") as f:
    calib_data = pickle.load(f)
    mtx = calib_data["mtx"]
    dist = calib_data["dist"]

# Configuración del stream
link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.20:554/stream1"
cap = cv2.VideoCapture(link)

if not cap.isOpened():
    print("Error al abrir la transmisión RTSP")
    exit()

# Configurar detector de blobs
params = cv2.SimpleBlobDetector_Params()
params.filterByColor = False  
params.filterByArea = True
params.minArea = 150
params.maxArea = 5000
params.filterByConvexity = False
params.minConvexity = 0.8
params.filterByCircularity = False
params.minCircularity = 0.7
params.filterByInertia = False

detector = cv2.SimpleBlobDetector_create(params)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al recibir el frame")
        break

    # Corrección de distorsión
    corrected = cv2.undistort(frame, mtx, dist, None, mtx)
    
    # Conversión a HSV y segmentación del LED rojo
    hsv = cv2.cvtColor(corrected, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 0, 240])
    upper_red1 = np.array([174, 255, 255])
    mask = cv2.inRange(hsv, lower_red1, upper_red1)
    mask = cv2.medianBlur(mask, 9)

    # Detección de blobs
    keypoints = detector.detect(mask)

    # Seleccionar solo el keypoint más grande
    if keypoints:
        keypoints = sorted(keypoints, key=lambda k: k.size, reverse=True)  # Ordenar por tamaño
        keypoints = [keypoints[0]]  # Solo el más grande

    # Dibujar el keypoint seleccionado
    result = corrected.copy()
    result = cv2.drawKeypoints(result, keypoints, None, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # Mostrar resultados
    cv2.imshow("Mascara Roja", mask)
    cv2.imshow("Detección de LED Rojo", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
