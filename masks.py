import cv2
import numpy as np
from collections import deque

# Ajustes
WIDTH, HEIGHT = 800, 400
FPS = 25  # Fijo para evitar errores con RTSP

# Inicializaciones
estela = deque(maxlen=10)
buffer_frames = deque(maxlen=int(FPS * 10))

cap = cv2.VideoCapture("rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2")

pts_src = np.load("esquinas.npy")
pts_dst = np.float32([
    [0, 0],
    [WIDTH - 1, 0],
    [WIDTH - 1, HEIGHT - 1],
    [0, HEIGHT - 1]
])
M = cv2.getPerspectiveTransform(pts_src, pts_dst)

if not cap.isOpened():
    print("Error al abrir RTSP")
    exit()

print("Presiona 'g' para guardar últimos 10s - 'q' para salir")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error leyendo frame")
        continue

    frame = cv2.warpPerspective(frame, M, (WIDTH, HEIGHT))

    # Detección
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, np.array([0, 76, 90]), np.array([179, 255, 255]))
    masked1 = cv2.bitwise_and(frame, frame, mask=mask1)
    mask2 = cv2.inRange(masked1, np.array([0, 0, 80]), np.array([140, 255, 255]))
    masked2 = cv2.bitwise_and(masked1, masked1, mask=mask2)

    blur = cv2.GaussianBlur(mask2, (9, 9), 0)
    kernel = np.ones((5, 5), np.uint8)
    clean = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pelota_detectada = False
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 200: continue
        perim = cv2.arcLength(cnt, True)
        if perim == 0: continue
        circularidad = 4 * np.pi * (area / (perim ** 2))
        if circularidad > 0.75:
            ((x, y), radio) = cv2.minEnclosingCircle(cnt)
            centro = (int(x), int(y))
            cv2.circle(frame, centro, int(radio), (0, 255, 0), 2)
            cv2.circle(frame, centro, 3, (0, 0, 255), -1)
            cv2.putText(frame, f"({int(x)}, {int(y)})", (int(x)+10, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            pelota_detectada = True
            estela.appendleft(centro)
            break
    if not pelota_detectada:
        estela.appendleft(None)

    for i in range(1, len(estela)):
        if estela[i - 1] and estela[i]:
            cv2.line(frame, estela[i - 1], estela[i], (255, 0, 255), 3)

    # Almacenar frame final en buffer
    buffer_frames.append(frame.copy())

    # Mostrar
    cv2.imshow("VAR", frame)
    #cv2.imshow("masked2", masked2)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('g'):
        if len(buffer_frames) < int(FPS * 3):  # Mínimo 3s de contenido
            print("Muy pocos frames para grabar. Espera unos segundos más.")
            continue

        print("Guardando últimos 10 segundos...")

        codec = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter("grabacion.mp4", codec, FPS, (WIDTH, HEIGHT))

        for f in buffer_frames:
            out.write(f)

        out.release()
        print("Grabado como 'grabacion.mp4'")

cap.release()
cv2.destroyAllWindows()
