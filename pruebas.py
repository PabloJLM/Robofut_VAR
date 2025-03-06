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
link = "rtsp://PabloJ1012:PabloJ1012@192.168.0.3:554/stream1"
Cam = cv2.VideoCapture(link, cv2.CAP_FFMPEG)

if not Cam.isOpened():
    print("Error al abrir la transmisión RTSP")
    exit()

# Optimización de la cámara
Cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Resolución más baja para mejorar rendimiento
Cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
Cam.set(cv2.CAP_PROP_BUFFERSIZE, 2)  
Cam.set(cv2.CAP_PROP_FPS, 15)  

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
    # Convertir a espacio de color HSV
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Definir rango de color rojo en HSV
    rojo_bajo = np.array([164, 135, 220])
    rojo_alto = np.array([179, 255, 255])
    rojo_mask = cv2.inRange(hsv, rojo_bajo, rojo_alto)

    # Detectar blobs blancos (en escala de grises)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    _, blanco_mask = cv2.threshold(gris, 250, 255, cv2.THRESH_BINARY)

    # Fusionar las máscaras
    fusion_mask = cv2.bitwise_or(rojo_mask, blanco_mask)

    return fusion_mask

# Bucle principal para capturar y procesar los fotogramas de la cámara
while True:
    # Saltar algunos fotogramas para reducir la latencia
    for _ in range(5): 
        Cam.grab()

    ret, frame = Cam.read()
    if not ret:
        print("Error al capturar el fotograma")
        break

    # Aplicar corrección de distorsión
    frame_corregido = cv2.undistort(frame, matriz, distorsion)

    # Obtener la máscara combinada
    fusion_mask = detectar_blobs(frame_corregido)
    # Aplicar Median Blur con un tamaño de kernel menor
    fusion_mask = cv2.medianBlur(fusion_mask, 5)  # Reducir el tamaño del kernel

    # Detectar blobs en la máscara combinada
    keypoints = detector.detect(fusion_mask)

    # Ordenar los blobs por tamaño (mayor a menor)
    keypoints_sorted = sorted(keypoints, key=lambda x: x.size, reverse=True)

    # Seleccionar solo los dos blobs más grandes
    if len(keypoints_sorted) >= 2:
        keypoints_sorted = keypoints_sorted[:2]
        etiquetas = ["LED_R1", "LED_R2"]

        # Dibujar los blobs detectados más grandes
        for i, blob in enumerate(keypoints_sorted):
            x, y = int(blob.pt[0]), int(blob.pt[1])
            print(f"{etiquetas[i]}: ({x}, {y})")  # Imprimir coordenadas en consola

            # Dibujar un círculo en el centro del blob
            cv2.circle(frame_corregido, (x, y), 5, (0, 255, 0), -1)

            radio = int(blob.size / 2)
            cv2.circle(frame_corregido, (x, y), radio, (0, 255, 0), 2)

            # Dibujar un texto para identificar el LED
            cv2.putText(frame_corregido, f"{etiquetas[i]}", 
                        (x + 10, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

    # Mostrar la imagen con los blobs detectados
    cv2.imshow('Blobs Detectados', frame_corregido)

    # Mostrar la máscara combinada
    cv2.imshow('Máscara Combinada', fusion_mask)

    # Salir del bucle al presionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q' or 'Q'):
        break

# Liberar la cámara y cerrar las ventanas
Cam.release()
cv2.destroyAllWindows()
