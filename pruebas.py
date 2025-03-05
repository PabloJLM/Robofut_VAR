import cv2
import pickle
import os
import numpy as np
#calibracion de la camara-----------------------------------------------------------------------------------------
archivo_calibracion = "calibration_data/calibration_matrices.p"
if not os.path.exists(archivo_calibracion):
    print(f"Error: No se encontró {archivo_calibracion}. Primero calibra la cámara.")
    exit()

with open(archivo_calibracion, "rb") as f:
    datos_calibracion = pickle.load(f)
    matriz = datos_calibracion["mtx"]
    distorsion = datos_calibracion["dist"]

#config cam -----------------------------------------------------------------------------------------------------
link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.3:554/stream1"
Cam = cv2.VideoCapture(link, cv2.CAP_FFMPEG)  

if not Cam.isOpened():
    print("Error al abrir la transmisión RTSP")
    exit()
#optimizacion de la CAM -------------------------------------------------------------------------------------------------
Cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
Cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
Cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)  
Cam.set(cv2.CAP_PROP_FPS, 15)  

#config de blobs---------------------------------------------------------------------------------------------------------------------------------------
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
#min max rojo --------------------------------------------------------------------------------
    rojo_min = np.array([0, 0, 255])  #bgr
    rojo_max = np.array([255, 110, 255]) #rgb
#min max azul --------------------------------------------------------------------------------    
    azul_bajo = np.array([220, 0, 0])  
    azul_alto = np.array([255, 150, 100])  

    mascara_roja = cv2.inRange(undist, rojo_min, rojo_max)
    mascara_roja = cv2.medianBlur(mascara_roja, 9) 
    
    mascara_azul = cv2.inRange(undist, azul_bajo, azul_alto)
    mascara_azul = cv2.medianBlur(mascara_azul, 9) 

    blobs_rojos = detector.detect(mascara_roja)
    blobs_azules = detector.detect(mascara_azul)

    final = undist.copy()
#rojo---------------------------------------------------------------------------------------------------------------------------
    if len(blobs_rojos) >= 2:
        blobs_rojos = sorted(blobs_rojos, key=lambda k: k.size, reverse=True)[:2]  #toma los 2 leds rojos 
        etiquetas = ["LED_R1", "LED_R2"]

        for i, blob in enumerate(blobs_rojos):
            x, y = int(blob.pt[0]), int(blob.pt[1])  
            print(f"{etiquetas[i]}: ({x}, {y})")  

            cv2.circle(final, (x, y), 5, (0, 255, 0), -1)  
            cv2.putText(final, f"{etiquetas[i]}", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0, 255, 0), 2, cv2.LINE_AA)
#azul-------------------------------------------------------------------------------------------------------------------            
    if len(blobs_azules) >= 2:
        blobs_azules = sorted(blobs_azules, key=lambda k: k.size, reverse=True)[:2]
        etiquetas_azules = ["LED_A1", "LED_A2"]

        for i, blob in enumerate(blobs_azules):
            x, y = int(blob.pt[0]), int(blob.pt[1])  
            print(f"{etiquetas_azules[i]}: ({x}, {y})")  
            cv2.circle(final, (x, y), 5, (0, 255, 255), -1)  
            cv2.putText(final, etiquetas_azules[i], (x + 10, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA)

    final = cv2.drawKeypoints(final, blobs_rojos, None, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    final = cv2.drawKeypoints(final, blobs_azules, None, (0, 255, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Detección de LED Rojo (RGB)", final)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

Cam.release()
cv2.destroyAllWindows()
