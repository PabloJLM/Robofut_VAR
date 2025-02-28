import cv2
import numpy as np

# Capturar video desde la cámara 1
cap = cv2.VideoCapture(1)

# Configurar detector de blobs
params = cv2.SimpleBlobDetector_Params()
params.filterByColor = True
params.blobColor = 255  # Detecta blobs en imágenes binarias
params.filterByArea = True
params.minArea = 10
params.maxArea = 500
params.filterByCircularity = False

# Crear el detector de blobs
detector = cv2.SimpleBlobDetector_create(params)

while True:
    # Leer el frame de la cámara
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir a HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Aplicar la máscara que diste
    mask1 = cv2.inRange(hsv, np.array([0, 150, 255]), np.array([179, 255, 255]))

    # Detectar blobs en la máscara
    keypoints = detector.detect(mask1)

    # Dibujar blobs en la imagen original
    frame_con_blobs = frame.copy()
    cv2.drawKeypoints(frame, keypoints, frame_con_blobs, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # Mostrar las imágenes
    cv2.imshow("Imagen Original", frame)
    cv2.imshow("Máscara", mask1)
    cv2.imshow("Blobs Detectados", frame_con_blobs)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
