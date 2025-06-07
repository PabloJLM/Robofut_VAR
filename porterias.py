import customtkinter
import cv2
import numpy as np
from PIL import Image, ImageTk

class VentanaPorterias(customtkinter.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Definir Líneas de Gol")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.canvas = customtkinter.CTkCanvas(self, width=800, height=500)
        self.canvas.pack(padx=10, pady=10, fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        self.puntos = []  # Esperamos 4 puntos (2 líneas)
        self.cap = cv2.VideoCapture("rtsp://PabloJ1012:PabloJ1012@192.168.1.109:554/stream2")
        self.after(100, self.actualizar_frame)

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.after(100, self.actualizar_frame)
            return

        # Dibujar líneas solo si hay pares completos
        if len(self.puntos) >= 2:
            cv2.line(frame, self.puntos[0], self.puntos[1], (0, 255, 0), 3)
            cv2.putText(frame, "Porteria A", self.puntos[0], cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        if len(self.puntos) == 4:
            cv2.line(frame, self.puntos[2], self.puntos[3], (0, 0, 255), 3)
            cv2.putText(frame, "Porteria B", self.puntos[2], cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((self.canvas.winfo_width(), self.canvas.winfo_height()))
        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)

        self.after(30, self.actualizar_frame)

    def on_click(self, event):
        if len(self.puntos) >= 4:
            return  # No más de 4 puntos

        # Coordenadas del click adaptadas al tamaño real del frame
        x = int(event.x * self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / self.canvas.winfo_width())
        y = int(event.y * self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / self.canvas.winfo_height())
        self.puntos.append((x, y))
        print(f"Punto {len(self.puntos)}: ({x}, {y})")

        if len(self.puntos) == 4:
            porterias = {
                "porteria_A": [self.puntos[0], self.puntos[1]],
                "porteria_B": [self.puntos[2], self.puntos[3]],
            }
            np.save("porterias.npy", porterias)
            print("Líneas guardadas en 'porterias.npy'")
            self.after(500, self.cerrar)

    def cerrar(self):
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()
