import cv2
import numpy as np
from collections import deque
from playsound import playsound
import threading
import os

# Config
WIDTH, HEIGHT = 800, 400
FPS = 25
DURACION = 10  # segundos antes del gol
FRAMES_UMBRAL = FPS * DURACION
FRAMES_EXTRA = 3 * FPS  # segundos después del gol

cap = cv2.VideoCapture("rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2")
buffer_frames = deque(maxlen=FRAMES_UMBRAL)


pts_src = np.load("esquinas.npy")
pts_dst = np.float32([
    [0, 0],
    [WIDTH - 1, 0],
    [WIDTH - 1, HEIGHT - 1],
    [0, HEIGHT - 1]
])
M = cv2.getPerspectiveTransform(pts_src, pts_dst)

porterias = np.load("porterias.npy", allow_pickle=True).item()
p1_A, p2_A = tuple(porterias["porteria_A"][0]), tuple(porterias["porteria_A"][1])
p1_B, p2_B = tuple(porterias["porteria_B"][0]), tuple(porterias["porteria_B"][1])


contador_A = 1
contador_B = 1
ultimo_gol_A = -FRAMES_UMBRAL
ultimo_gol_B = -FRAMES_UMBRAL
lado_anterior_A = None
lado_anterior_B = None
frames_post_A = []
frames_post_B = []
post_gol_restante_A = 0
post_gol_restante_B = 0
frame_actual = 0


def punto_cruza_linea(punto, p1, p2):
    A, B, P = np.array(p1), np.array(p2), np.array(punto)
    AB, AP = B - A, P - A
    return np.cross(AB, AP) > 0

# Sonido
def reproducir_sonido():
    sonido = os.path.join(os.path.dirname(__file__), "gol.mp3")
    threading.Thread(target=playsound, args=(sonido,), daemon=True).start()

print("Presiona 'q' para salir")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error leyendo frame")
        continue

    frame = cv2.warpPerspective(frame, M, (WIDTH, HEIGHT))

    cv2.line(frame, p1_A, p2_A, (0, 255, 0), 2)
    cv2.putText(frame, "Porteria A", p1_A, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.line(frame, p1_B, p2_B, (255, 0, 0), 2)
    cv2.putText(frame, "Porteria B", p1_B, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

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
            break

    # Detectar cruce en A
    if centro:
        lado_actual_A = punto_cruza_linea(centro, p1_A, p2_A)
        if lado_anterior_A is not None and lado_actual_A != lado_anterior_A:
            if frame_actual - ultimo_gol_A >= FRAMES_UMBRAL:
                print("Gol en Portería A")
                post_gol_restante_A = FRAMES_EXTRA
                ultimo_gol_A = frame_actual
                reproducir_sonido()
        lado_anterior_A = lado_actual_A

        # Detectar cruce en B
        lado_actual_B = punto_cruza_linea(centro, p1_B, p2_B)
        if lado_anterior_B is not None and lado_actual_B != lado_anterior_B:
            if frame_actual - ultimo_gol_B >= FRAMES_UMBRAL:
                print("Gol en Portería B")
                post_gol_restante_B = FRAMES_EXTRA
                ultimo_gol_B = frame_actual
                reproducir_sonido()
        lado_anterior_B = lado_actual_B

    # Agregar al buffer
    buffer_frames.append(frame.copy())

    # Post-gol A
    if post_gol_restante_A > 0:
        frames_post_A.append(frame.copy())
        post_gol_restante_A -= 1
        if post_gol_restante_A == 0:
            nombre = f"grabacion{contador_A}A.mp4"
            print(f"Guardando {nombre}")
            out = cv2.VideoWriter(nombre, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
            for f in buffer_frames: out.write(f)
            for f in frames_post_A: out.write(f)
            out.release()
            print("Guardado A")
            contador_A += 1
            frames_post_A.clear()

    # Post-gol B
    if post_gol_restante_B > 0:
        frames_post_B.append(frame.copy())
        post_gol_restante_B -= 1
        if post_gol_restante_B == 0:
            nombre = f"grabacion{contador_B}B.mp4"
            print(f"Guardando {nombre}")
            out = cv2.VideoWriter(nombre, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
            for f in buffer_frames: out.write(f)
            for f in frames_post_B: out.write(f)
            out.release()
            print("Guardado B")
            contador_B += 1
            frames_post_B.clear()

    # Mostrar
    cv2.imshow("VAR", frame)
    frame_actual += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
import cv2
import numpy as np
from collections import deque
from playsound import playsound
import threading

# Configuración
WIDTH, HEIGHT = 800, 400
FPS = 25
DURACION = 10  # segundos antes del gol
FRAMES_UMBRAL = FPS * DURACION
FRAMES_EXTRA = 3 * FPS  # segundos después del gol

# Inicialización
cap = cv2.VideoCapture("rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2")
buffer_frames = deque(maxlen=FRAMES_UMBRAL)

# Cargar esquinas y homografía
pts_src = np.load("esquinas.npy")
pts_dst = np.float32([
    [0, 0],
    [WIDTH - 1, 0],
    [WIDTH - 1, HEIGHT - 1],
    [0, HEIGHT - 1]
])
M = cv2.getPerspectiveTransform(pts_src, pts_dst)

# Cargar porterías
porterias = np.load("porterias.npy", allow_pickle=True).item()
p1_A, p2_A = tuple(porterias["porteria_A"][0]), tuple(porterias["porteria_A"][1])
p1_B, p2_B = tuple(porterias["porteria_B"][0]), tuple(porterias["porteria_B"][1])

# Estados
contador_A = 1
contador_B = 1
ultimo_gol_A = -FRAMES_UMBRAL
ultimo_gol_B = -FRAMES_UMBRAL
lado_anterior_A = None
lado_anterior_B = None
frames_post_A = []
frames_post_B = []
post_gol_restante_A = 0
post_gol_restante_B = 0
frame_actual = 0

# Función cruce
def punto_cruza_linea(punto, p1, p2):
    A, B, P = np.array(p1), np.array(p2), np.array(punto)
    AB, AP = B - A, P - A
    return np.cross(AB, AP) > 0

# Sonido (en hilo aparte para no trabar video)
def reproducir_sonido():
    threading.Thread(target=playsound, args=("gol.mp3",), daemon=True).start()

print("Presiona 'q' para salir")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error leyendo frame")
        continue

    frame = cv2.warpPerspective(frame, M, (WIDTH, HEIGHT))

    # Dibujar porterías
    cv2.line(frame, p1_A, p2_A, (0, 255, 0), 2)
    cv2.putText(frame, "Porteria A", p1_A, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.line(frame, p1_B, p2_B, (255, 0, 0), 2)
    cv2.putText(frame, "Porteria B", p1_B, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

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
            break

    # Detectar cruce en A
    if centro:
        lado_actual_A = punto_cruza_linea(centro, p1_A, p2_A)
        if lado_anterior_A is not None and lado_actual_A != lado_anterior_A:
            if frame_actual - ultimo_gol_A >= FRAMES_UMBRAL:
                print("Gol en Portería A")
                post_gol_restante_A = FRAMES_EXTRA
                ultimo_gol_A = frame_actual
                reproducir_sonido()
        lado_anterior_A = lado_actual_A

        # Detectar cruce en B
        lado_actual_B = punto_cruza_linea(centro, p1_B, p2_B)
        if lado_anterior_B is not None and lado_actual_B != lado_anterior_B:
            if frame_actual - ultimo_gol_B >= FRAMES_UMBRAL:
                print("Gol en Portería B")
                post_gol_restante_B = FRAMES_EXTRA
                ultimo_gol_B = frame_actual
                reproducir_sonido()
        lado_anterior_B = lado_actual_B

    # Agregar al buffer
    buffer_frames.append(frame.copy())

    # Post-gol A
    if post_gol_restante_A > 0:
        frames_post_A.append(frame.copy())
        post_gol_restante_A -= 1
        if post_gol_restante_A == 0:
            nombre = f"grabacion{contador_A}A.mp4"
            print(f"Guardando {nombre}")
            out = cv2.VideoWriter(nombre, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
            for f in buffer_frames: out.write(f)
            for f in frames_post_A: out.write(f)
            out.release()
            print("✅ Guardado A")
            contador_A += 1
            frames_post_A.clear()

    # Post-gol B
    if post_gol_restante_B > 0:
        frames_post_B.append(frame.copy())
        post_gol_restante_B -= 1
        if post_gol_restante_B == 0:
            nombre = f"grabacion{contador_B}B.mp4"
            print(f"💾 Guardando {nombre}")
            out = cv2.VideoWriter(nombre, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
            for f in buffer_frames: out.write(f)
            for f in frames_post_B: out.write(f)
            out.release()
            print("✅ Guardado B")
            contador_B += 1
            frames_post_B.clear()

    # Mostrar
    cv2.imshow("VAR", frame)
    frame_actual += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
