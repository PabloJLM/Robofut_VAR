import cv2
import numpy as np
import pickle
import os

# Cargar la calibración de la cámara
archivo_calibracion = "calibration_data/calibration_matrices.p"
if not os.path.exists(archivo_calibracion):
    print(f"Error: No se encontró {archivo_calibracion}. Primero calibra la cámara.")
    exit()

with open(archivo_calibracion, "rb") as f:
    datos_calibracion = pickle.load(f)
    matriz = datos_calibracion["mtx"]
    distorsion = datos_calibracion["dist"]

# Configuración de la cámara
link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.3:554/stream2"
Cam = cv2.VideoCapture(link, cv2.CAP_FFMPEG)

if not Cam.isOpened():
    print("Error al abrir la transmisión RTSP")
    exit()

# Optimización de la cámara
Cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  
Cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
Cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)  
Cam.set(cv2.CAP_PROP_FPS, 30)  # FPS real de la cámara

# Parámetros de detección de blobs
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

# Función para detectar blobs usando la máscara combinada
def detectar_blobs(imagen):
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    
    # Definir rango de color rojo en HSV
    rojo_bajo = np.array([164, 135, 220])
    rojo_alto = np.array([179, 255, 255])
    rojo_mask = cv2.inRange(hsv, rojo_bajo, rojo_alto)

    # Aplicar dilatación en lugar de blur para mejorar detección
    kernel = np.ones((9, 9), np.uint8)
    fusion_mask = cv2.dilate(rojo_mask, kernel, iterations=1)

    return fusion_mask

frame_count = 0  # Contador de frames
keypoints_mem = []  # Almacenar blobs detectados
etiquetas = ["LED_R1", "LED_R2"]

# Bucle principal para capturar y mostrar los fotogramas
while True:
    ret, frame = Cam.read()
    if not ret:
        print("Error al capturar el fotograma")
        break

    # Aplicar corrección de distorsión
    frame_corregido = cv2.undistort(frame, matriz, distorsion, None, matriz)

    # Procesar blobs solo cada 5 frames
    if frame_count % 5 == 0:
        fusion_mask = detectar_blobs(frame_corregido)
        keypoints = detector.detect(fusion_mask)

        # Guardamos los blobs detectados en memoria
        keypoints_mem = sorted(keypoints, key=lambda x: x.size, reverse=True)[:2]

    # Dibujar blobs detectados en todos los frames (para fluidez)
    for i, blob in enumerate(keypoints_mem):
        x, y = int(blob.pt[0]), int(blob.pt[1])
        
        # Dibujar punto y círculo
        cv2.circle(frame_corregido, (x, y), 5, (0, 255, 0), -1)
        radio = int(blob.size / 2)
        cv2.circle(frame_corregido, (x, y), radio, (0, 255, 0), 2)

        # Dibujar texto con fondo negro para mejor visibilidad
        texto = f"{etiquetas[i]}: ({x}, {y})"
        (text_w, text_h), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(frame_corregido, (x, y - 15), (x + text_w, y), (0, 0, 0), -1)
        cv2.putText(frame_corregido, texto, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

    # Mostrar el video en tiempo real
    cv2.imshow('Blobs Detectados', frame_corregido)

    frame_count += 1  # Aumentar contador de frames

    # Salir del bucle al presionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
Cam.release()
cv2.destroyAllWindows()
