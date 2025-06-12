import cv2
import numpy as np
from collections import deque
import threading
import pygame

WIDTH, HEIGHT = 800, 400
FPS = 25
DURACION = 10
FRAMES_UMBRAL = FPS * DURACION
FRAMES_EXTRA = 3 * FPS
VIDEO_PATH = "rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2"
SONIDO_GOL = "C:/Users/pablo/OneDrive/Escritorio/Yo/fut/gol.mp3"

def reproducir_sonido():
    pygame.mixer.init()
    pygame.mixer.music.load("gol.mp3")
    pygame.mixer.music.play()

def cruzo_linea(punto_actual, punto_anterior, p1, p2):
    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    return (ccw(punto_anterior, p1, p2) != ccw(punto_actual, p1, p2)) and (ccw(punto_anterior, punto_actual, p1) != ccw(punto_anterior, punto_actual, p2))

def detectar_pelota(frame_aplanado, kernel):
    hsv = cv2.cvtColor(frame_aplanado, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, (0, 76, 90), (179, 255, 255))
    masked1 = cv2.bitwise_and(frame_aplanado, frame_aplanado, mask=mask1)
    mask2 = cv2.inRange(masked1, (0, 0, 80), (140, 255, 255))
    blur = cv2.GaussianBlur(mask2, (9, 9), 0)
    clean = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in sorted(contours, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(cnt)
        if area < 250: continue
        perim = cv2.arcLength(cnt, True)
        if perim == 0: continue
        circularidad = 4 * np.pi * (area / (perim ** 2))
        if circularidad > 0.77:
            ((x, y), radio) = cv2.minEnclosingCircle(cnt)
            centro = (int(x), int(y))
            return centro, int(radio), clean
    return None, 0, clean

def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    buffer_frames = deque(maxlen=FRAMES_UMBRAL)
    frame_actual = 0
    kernel = np.ones((5, 5), np.uint8)

    pts_src = np.load("esquinas.npy")
    pts_dst = np.float32([[0, 0], [WIDTH-1, 0], [WIDTH-1, HEIGHT-1], [0, HEIGHT-1]])
    M = cv2.getPerspectiveTransform(pts_src, pts_dst)

    porterias = np.load("porterias.npy", allow_pickle=True).item()
    p1_A, p2_A = map(tuple, porterias["porteria_A"])
    p1_B, p2_B = map(tuple, porterias["porteria_B"])
    contador_A = contador_B = 1
    ultimo_gol_A = ultimo_gol_B = -FRAMES_UMBRAL
    post_gol_restante_A = post_gol_restante_B = 0
    frames_post_A = []
    frames_post_B = []
    pelota_anterior = None

    while True:
        ret, frame = cap.read()
        if not ret: continue
        frame_aplanado = cv2.warpPerspective(frame, M, (WIDTH, HEIGHT))

        cv2.line(frame_aplanado, p1_A, p2_A, (0,255,0), 2)
        cv2.line(frame_aplanado, p1_B, p2_B, (255,0,0), 2)

        centro, radio, mask_clean = detectar_pelota(frame_aplanado, kernel)
        if centro:
            cv2.circle(frame_aplanado, centro, radio, (0,255,0), 2)
            cv2.circle(frame_aplanado, centro, 3, (0,0,255), -1)

            if pelota_anterior:
                if cruzo_linea(centro, pelota_anterior, p1_A, p2_A) and frame_actual - ultimo_gol_A >= FRAMES_UMBRAL:
                    print("¡GOL en Portería A!")
                    reproducir_sonido()
                    post_gol_restante_A = FRAMES_EXTRA
                    ultimo_gol_A = frame_actual

                if cruzo_linea(centro, pelota_anterior, p1_B, p2_B) and frame_actual - ultimo_gol_B >= FRAMES_UMBRAL:
                    print("¡GOL en Portería B!")
                    reproducir_sonido()
                    post_gol_restante_B = FRAMES_EXTRA
                    ultimo_gol_B = frame_actual

            pelota_anterior = centro

        buffer_frames.append(frame_aplanado.copy())

        if post_gol_restante_A > 0:
            frames_post_A.append(frame_aplanado.copy())
            post_gol_restante_A -= 1
            if post_gol_restante_A == 0:
                nombre = f"grabacion{contador_A}A.mp4"
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
                out = cv2.VideoWriter(nombre, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH, HEIGHT))
                for f in buffer_frames: out.write(f)
                for f in frames_post_B: out.write(f)
                out.release()
                contador_B += 1
                frames_post_B.clear()

        cv2.imshow("VAR", frame_aplanado)
        cv2.imshow("Pelota Limpia", mask_clean)
        frame_actual += 1
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
