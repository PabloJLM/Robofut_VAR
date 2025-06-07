import cv2
import numpy as np
from collections import deque
import os

# Ajustes
WIDTH, HEIGHT = 800, 400
FPS = 25
DURACION = 10  # segundos de grabación
FRAMES_UMBRAL = FPS * DURACION

# Inicializaciones
buffer_frames = deque(maxlen=FRAMES_UMBRAL)
cap = cv2.VideoCapture("rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2")

# Homografía
pts_src = np.load("esquinas.npy")
pts_dst = np.float32([
    [0, 0],
    [WIDTH - 1, 0],
    [WIDTH - 1, HEIGHT - 1],
    [0, HEIGHT - 1]
])
M = cv2.getPerspectiveTransform(pts_src, pts_dst)

# Cargar portería A
porterias = np.load("porterias.npy", allow_pickle=True).item()
p1, p2 = tuple(porterias["porteria_A"][0]), tuple(porterias["porteria_A"][1])

# Estado de grabación
contador_goles_A = 1
ultimo_frame_gol = -FRAMES_UMBRAL
frame_actual = 0

print("Presiona 'q' para salir")

# Función para verificar si un punto está al otro lado de una línea
def punto_cruza_linea(punto, linea_p1, linea_p2):
    A = np.array(linea_p1)
    B = np.array(linea_p2)
    P = np.array(punto)
    AB = B - A
    AP = P - A
    cross = np.cross(AB, AP)
    return cross > 0  # o < 0 dependiendo de orientación

# Valor anterior del lado para detectar cruce
lado_anterior = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error leyendo frame")
        continue

    frame = cv2.warpPerspective(frame, M, (WIDTH, HEIGHT))

    # Dibujar portería
    cv2.line(frame, p1, p2, (0, 255, 0), 2)
    cv2.putText(frame, "Porteria A", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # Detección de pelota
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, np.array([0, 76, 90]), np.array([179, 255, 255]))
    masked1 = cv2.bitwise_and(frame, frame, mask=mask1)
    mask2 = cv2.inRange(masked1, np.array([0, 0, 80]), np.array([140, 255, 255]))
    blur = cv2.GaussianBlur(mask2, (9, 9), 0)
    kernel = np.ones((5, 5), np.uint8)
    clean = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centro = None
    cruzo_porteria = False

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

            # Verificar cruce con línea
            lado_actual = punto_cruza_linea(centro, p1, p2)

            if lado_anterior is not None and lado_actual != lado_anterior:
                cruzo_porteria = True
                break  # Ya encontramos cruce, no necesitamos más

            lado_anterior = lado_actual
            break  # Solo tomamos la pelota más circular

    # Grabar si cruzó la portería y han pasado suficientes frames desde el último gol
    if cruzo_porteria and frame_actual - ultimo_frame_gol >= FRAMES_UMBRAL:
        nombre = f"grabacion{contador_goles_A}A.mp4"
        print(f"Gol en Portería A → guardando como {nombre}")
        codec = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(nombre, codec, FPS, (WIDTH, HEIGHT))
        for f in buffer_frames:
            out.write(f)
        out.release()
        print(f"Guardado correctamente")
        contador_goles_A += 1
        ultimo_frame_gol = frame_actual

    # Guardar frame en buffer
    buffer_frames.append(frame.copy())

    # Mostrar
    cv2.imshow("VAR", frame)
    frame_actual += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
