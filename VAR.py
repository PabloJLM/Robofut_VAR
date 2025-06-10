import cv2
import numpy as np
from collections import deque
from playsound import playsound
import threading
import os

# Configuraciones
WIDTH, HEIGHT = 800, 400
FPS = 25
DURACION = 10
FRAMES_UMBRAL = FPS * DURACION
FRAMES_EXTRA = 3 * FPS

max_objetos_verde = 1
max_objetos_rojo = 1

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

def reproducir_sonido():
    sonido = os.path.join(os.path.dirname(__file__), "gol.mp3")
    threading.Thread(target=playsound, args=(sonido,), daemon=True).start()

print("Presiona 'q' para salir")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error leyendo frame")
        continue

    frame_aplanado = cv2.warpPerspective(frame, M, (WIDTH, HEIGHT))
    frame_leds = frame.copy()

    # === Detección de LEDs en frame original ===
    hsv = cv2.cvtColor(frame_leds, cv2.COLOR_BGR2HSV)
    low_hsv = np.array([0, 76, 90])
    up_hsv = np.array([179, 255, 255])
    mask_hsv = cv2.inRange(hsv, low_hsv, up_hsv)
    result_hsv = cv2.bitwise_and(frame_leds, frame_leds, mask=mask_hsv)

    blurred = cv2.GaussianBlur(result_hsv, (9, 9), 0)
    kernel = np.ones((5, 5), np.uint8)
    limpieza = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel)
    limpieza_rgb = cv2.cvtColor(limpieza, cv2.COLOR_BGR2RGB)

    # Detección verde
    verde_bajo = np.array([0, 138, 0])
    verde_alto = np.array([104, 255, 150])
    mask_verde = cv2.inRange(limpieza_rgb, verde_bajo, verde_alto)
    contornos_verde, _ = cv2.findContours(mask_verde, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_verde = sorted(contornos_verde, key=cv2.contourArea, reverse=True)[:max_objetos_verde]

    for cnt in contornos_verde:
        if cv2.contourArea(cnt) < 50: 
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w//2, y + h//2
        punto = np.array([[[cx, cy]]], dtype='float32')
        transformado = cv2.perspectiveTransform(punto, M)[0][0]
        cv2.circle(frame_aplanado, tuple(map(int, transformado)), 6, (0,255,0), -1)
        cv2.putText(frame_aplanado, f"V({int(transformado[0])},{int(transformado[1])})", 
                    (int(transformado[0])+10, int(transformado[1])), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # Detección roja
    rojo_bajo = np.array([215, 86, 0])
    rojo_alto = np.array([255, 140, 180])
    mask_rojo = cv2.inRange(limpieza_rgb, rojo_bajo, rojo_alto)
    contornos_rojo, _ = cv2.findContours(mask_rojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_rojo = sorted(contornos_rojo, key=cv2.contourArea, reverse=True)[:max_objetos_rojo]

    for cnt in contornos_rojo:
        if cv2.contourArea(cnt) < 50: 
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w//2, y + h//2
        punto = np.array([[[cx, cy]]], dtype='float32')
        transformado = cv2.perspectiveTransform(punto, M)[0][0]
        cv2.circle(frame_aplanado, tuple(map(int, transformado)), 6, (0,0,255), -1)
        cv2.putText(frame_aplanado, f"R({int(transformado[0])},{int(transformado[1])})", 
                    (int(transformado[0])+10, int(transformado[1])), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # === Dibujo porterías en aplanado ===
    cv2.line(frame_aplanado, p1_A, p2_A, (0, 255, 0), 2)
    cv2.putText(frame_aplanado, "Porteria A", p1_A, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.line(frame_aplanado, p1_B, p2_B, (255, 0, 0), 2)
    cv2.putText(frame_aplanado, "Porteria B", p1_B, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

    # === Detección pelota en aplanado (solo una pelota) ===
    hsv_apl = cv2.cvtColor(frame_aplanado, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv_apl, np.array([0, 76, 90]), np.array([179, 255, 255]))
    masked1 = cv2.bitwise_and(frame_aplanado, frame_aplanado, mask=mask1)
    mask2 = cv2.inRange(masked1, np.array([0, 0, 80]), np.array([140, 255, 255]))
    blur = cv2.GaussianBlur(mask2, (9, 9), 0)
    clean = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Ordenar por área descendente, tomar solo la mayor (la pelota más probable)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    centro = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 250:
            continue
        perim = cv2.arcLength(cnt, True)
        if perim == 0:
            continue
        circularidad = 4 * np.pi * (area / (perim ** 2))
        if circularidad > 0.77:
            ((x, y), radio) = cv2.minEnclosingCircle(cnt)
            centro = (int(x), int(y))
            cv2.circle(frame_aplanado, centro, int(radio), (0, 255, 0), 2)
            cv2.circle(frame_aplanado, centro, 3, (0, 0, 255), -1)
            break  # Solo la primera pelota detectada

    # Gol A
    if centro:
        lado_actual_A = punto_cruza_linea(centro, p1_A, p2_A)
        if lado_anterior_A is not None and lado_actual_A != lado_anterior_A:
            if frame_actual - ultimo_gol_A >= FRAMES_UMBRAL:
                print("Gol en Portería A")
                post_gol_restante_A = FRAMES_EXTRA
                ultimo_gol_A = frame_actual
                reproducir_sonido()
        lado_anterior_A = lado_actual_A

        # Gol B
        lado_actual_B = punto_cruza_linea(centro, p1_B, p2_B)
        if lado_anterior_B is not None and lado_actual_B != lado_anterior_B:
            if frame_actual - ultimo_gol_B >= FRAMES_UMBRAL:
                print("Gol en Portería B")
                post_gol_restante_B = FRAMES_EXTRA
                ultimo_gol_B = frame_actual
                reproducir_sonido()
        lado_anterior_B = lado_actual_B

    buffer_frames.append(frame_aplanado.copy())

    if post_gol_restante_A > 0:
        frames_post_A.append(frame_aplanado.copy())
        post_gol_restante_A -= 1
        if post_gol_restante_A == 0:
            nombre = f"grabacion{contador_A}A.mp4"
            print(f"Guardando {nombre}")
            out = cv2.VideoWriter(nombre, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
            for f in buffer_frames: out.write(f)
            for f in frames_post_A: out.write(f)
            out.release()
            contador_A += 1
            frames_post_A.clear()

    if post_gol_restante_B > 0:
        frames_post_B.append(frame_aplanado.copy())
        post_gol_restante_B -= 1
        if post_gol_restante_B == 0:
            nombre = f"grabacion{contador_B}B.mp4"
            print(f"Guardando {nombre}")
            out = cv2.VideoWriter(nombre, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
            for f in buffer_frames: out.write(f)
            for f in frames_post_B: out.write(f)
            out.release()
            contador_B += 1
            frames_post_B.clear()

    cv2.imshow("VAR", frame_aplanado)
    cv2.imshow("vista", clean)
    cv2.imshow("m1", clean)
    cv2.imshow("m2", clean)
    frame_actual += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
