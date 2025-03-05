import cv2
import pickle
import os
import numpy as np

archivo_calibracion = "calibration_data/calibration_matrices.p"
if not os.path.exists(archivo_calibracion):
    print(f"Error: No se encontró {archivo_calibracion}. Primero calibra la cámara.")
    exit()

with open(archivo_calibracion, "rb") as f:
    datos_calibracion = pickle.load(f)
    matriz = datos_calibracion["mtx"]
    distorsion = datos_calibracion["dist"]

link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.3:554/stream1"
Cam = cv2.VideoCapture(link, cv2.CAP_FFMPEG)  

if not Cam.isOpened():
    print("Error al abrir la transmisión RTSP")
    exit()

Cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
Cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
Cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)  
Cam.set(cv2.CAP_PROP_FPS, 30)  

parametros = cv2.SimpleBlobDetector_Params()
parametros.filterByColor = False  
parametros.filterByArea = True
parametros.minArea = 150
parametros.maxArea = 5000
parametros.filterByConvexity = False
parametros.minConvexity = 0.8
parametros.filterByCircularity = False
parametros.minCircularity = 0.7
parametros.filterByInertia = False

detector = cv2.SimpleBlobDetector_create(parametros)

while Cam.isOpened():
    for _ in range(5): 
        Cam.grab()

    ret, frame = Cam.read()
    if not ret:
        print("Error al recibir el fotograma")
        break

    undist = cv2.undistort(frame, matriz, distorsion, None, matriz)

    rojo_min = np.array([0, 0, 220])  
    rojo_max = np.array([220, 150, 255])  

    mask = cv2.inRange(undist, rojo_min, rojo_max)
    mask = cv2.medianBlur(mask, 9)  

    blobs = detector.detect(mask)

    final = undist.copy()

    if len(blobs) >= 2:
        blobs = sorted(blobs, key=lambda k: k.size, reverse=True)[:2]  #toma los 2 leds rojos 
        etiquetas = ["LED1", "LED2"]

        for i, blob in enumerate(blobs):
            x, y = int(blob.pt[0]), int(blob.pt[1])  
            print(f"{etiquetas[i]}: ({x}, {y})")  

            cv2.circle(final, (x, y), 5, (0, 255, 0), -1)  
            cv2.putText(final, f"{etiquetas[i]}", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0, 255, 0), 2, cv2.LINE_AA)

    final = cv2.drawKeypoints(final, blobs, None, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Detección de LED Rojo (RGB)", final)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

Cam.release()
cv2.destroyAllWindows()
