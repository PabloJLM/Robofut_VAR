import customtkinter
import cv2
import numpy as np
from collections import deque
from PIL import Image, ImageTk

class VAR(customtkinter.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("VAR")
        self.geometry("900x620")

        self.canvas = customtkinter.CTkCanvas(self, width=800, height=500)
        self.canvas.pack(padx=10, pady=(10, 5))

        self.boton_guardar = customtkinter.CTkButton(self, text="💾 Guardar últimos 10s", command=self.guardar_clip)
        self.boton_guardar.pack(pady=(0, 10))

        self.buffer_frames = deque(maxlen=300)  # ~10s si FPS = 30

        self.cap = cv2.VideoCapture("rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2")
        if not self.cap.isOpened():
            print("Error al abrir la transmisión RTSP")
            self.destroy()
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.width, self.height = 800, 400

        pts_src = np.load("esquinas.npy")
        pts_dst = np.float32([
            [0, 0],
            [self.width - 1, 0],
            [self.width - 1, self.height - 1],
            [0, self.height - 1]
        ])
        self.M = cv2.getPerspectiveTransform(pts_src, pts_dst)
        self.estela = deque(maxlen=10)

        self.after(30, self.actualizar_frame)

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.after(100, self.actualizar_frame)
            return

        # Aplanar el campo (homografía)
        frame = cv2.warpPerspective(frame, self.M, (self.width, self.height))
        
        # Guardar copia para el buffer antes de dibujar (para tener video limpio)
        self.buffer_frames.append(frame.copy())

        # --- Detección de pelota ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        low1 = np.array([0, 76, 90])
        up1 = np.array([179, 255, 255])
        low2 = np.array([0, 0, 80])
        up2 = np.array([140, 255, 255])

        mask1 = cv2.inRange(hsv, low1, up1)
        masked1 = cv2.bitwise_and(frame, frame, mask=mask1)
        mask2 = cv2.inRange(masked1, low2, up2)
        masked2 = cv2.bitwise_and(masked1, masked1, mask=mask2)

        gblur = cv2.GaussianBlur(mask2, (9, 9), 0)
        kernel = np.ones((5, 5), np.uint8)
        clean = cv2.morphologyEx(gblur, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        pelota_detectada = False

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 200:
                continue
            perim = cv2.arcLength(cnt, True)
            if perim == 0:
                continue
            circularidad = 4 * np.pi * (area / (perim ** 2))
            if circularidad > 0.75:
                ((x, y), radio) = cv2.minEnclosingCircle(cnt)
                centro = (int(x), int(y))
                cv2.circle(frame, centro, int(radio), (0, 255, 0), 2)
                cv2.circle(frame, centro, 3, (0, 0, 255), -1)
                cv2.putText(frame, f"({int(x)}, {int(y)})", (int(x)+10, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                pelota_detectada = True
                self.estela.appendleft(centro)
                break

        if not pelota_detectada:
            self.estela.appendleft(None)

        # Dibujar estela
        for i in range(1, len(self.estela)):
            if self.estela[i - 1] and self.estela[i]:
                cv2.line(frame, self.estela[i - 1], self.estela[i], (255, 0, 255), 3)

        # --- Mostrar solo copia escalada en la GUI ---
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)

        # Redimensionar solo para visualización en GUI
        display_width = self.canvas.winfo_width()
        display_height = self.canvas.winfo_height()
        if display_width > 0 and display_height > 0:
            img_pil = img_pil.resize((display_width, display_height), Image.Resampling.LANCZOS)

        self.img_tk = ImageTk.PhotoImage(img_pil)
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)

        self.after(30, self.actualizar_frame)


    def guardar_clip(self):
        if not self.buffer_frames:
            print("No hay frames en el buffer")
            return

        print("Guardando los últimos 10 segundos...")

        codec = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter("grabacion.mp4", codec, self.fps, (self.width, self.height))

        for frame in self.buffer_frames:
            out.write(frame)

        out.release()
        print("Clip guardado como 'grabacion.mp4'")

    def destroy(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        super().destroy()
