import customtkinter
from tkinter import filedialog, messagebox
from PIL import Image
import os
import cv2
import threading
import time

class VentanaGrabaciones(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Grabaciones VAR")
        self.geometry("900x750")
        self.configure(fg_color="#1b1f2b")

        self.var_folder = None
        self.video_label = None
        self.video_thread = None
        self.cap = None
        self.running = False
        self.paused = False
        self.velocidad = 1.0  # Velocidad inicial (1x)

        self.label = customtkinter.CTkLabel(self, text="Selecciona la carpeta de grabaciones", font=("Arial", 16))
        self.label.pack(pady=10)

        self.boton_seleccionar = customtkinter.CTkButton(self, text="Seleccionar carpeta", command=self.seleccionar_carpeta)
        self.boton_seleccionar.pack(pady=5)

        # Marco del video
        self.video_frame = customtkinter.CTkFrame(self, height=360, width=640)
        self.video_frame.pack(pady=10)
        self.video_label = customtkinter.CTkLabel(self.video_frame, text="")
        self.video_label.pack()

        # Controles de reproducción
        controles_frame = customtkinter.CTkFrame(self)
        controles_frame.pack(pady=5)

        self.boton_pausa = customtkinter.CTkButton(controles_frame, text="Pausar", command=self.toggle_pausa)
        self.boton_pausa.pack(side="left", padx=10)

        self.selector_velocidad = customtkinter.CTkOptionMenu(controles_frame, values=["0.5x", "1x", "1.5x", "2x"], command=self.cambiar_velocidad)
        self.selector_velocidad.set("1x")
        self.selector_velocidad.pack(side="left", padx=10)

        # Scroll 
        self.scroll = customtkinter.CTkScrollableFrame(self, width=850, height=280)
        self.scroll.pack(pady=10, expand=True)

        self.boton_refrescar = customtkinter.CTkButton(self, text="Refrescar lista", command=self.mostrar_videos)
        self.boton_refrescar.pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

    def seleccionar_carpeta(self):
        ruta = filedialog.askdirectory(title="Selecciona carpeta que contenga grabaciones")
        if ruta:
            self.var_folder = ruta
            self.mostrar_videos()
    
    def cerrar_ventana(self):
        self.cerrar_video()
        self.destroy()

    def mostrar_videos(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not self.var_folder:
            messagebox.showwarning("Atención", "Primero selecciona una carpeta.")
            return

        archivos = [f for f in os.listdir(self.var_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

        if not archivos:
            customtkinter.CTkLabel(self.scroll, text="No hay videos en esta carpeta.", font=("Arial", 14)).pack(pady=10)
            return

        for archivo in archivos:
            ruta_video = os.path.join(self.var_folder, archivo)
            img = self.generar_miniatura_memoria(ruta_video)
            if img is None:
                continue

            img_ctk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(160, 90))

            frame = customtkinter.CTkFrame(self.scroll)
            frame.pack(padx=10, pady=5, fill="x")

            label = customtkinter.CTkLabel(frame, image=img_ctk, text="", width=160, height=90)
            label.image = img_ctk
            label.pack(side="left", padx=10)

            boton = customtkinter.CTkButton(frame, text=archivo, command=lambda r=ruta_video: self.reproducir_video(r), width=600, anchor="w")
            boton.pack(side="left", fill="x", expand=True, padx=5)

    def generar_miniatura_memoria(self, video_path, tamaño=(160, 90)):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_n = total_frames // 4
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_n)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize(tamaño, Image.Resampling.LANCZOS)
        return img

    def reproducir_video(self, ruta_video):
        self.cerrar_video()
        self.cap = cv2.VideoCapture(ruta_video)
        self.running = True
        self.paused = False
        self.boton_pausa.configure(text="Pausar")
        self.video_thread = threading.Thread(target=self.actualizar_frame, daemon=True)
        self.video_thread.start()

    def actualizar_frame(self):
        while self.running and self.cap and self.cap.isOpened():
            if not self.paused:
                ret, frame = self.cap.read()
                if not ret:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 360))
                img = Image.fromarray(frame)
                img_tk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(640, 360))
                self.video_label.configure(image=img_tk)
                self.video_label.image = img_tk
                self.update_idletasks()
            time.sleep(1 / (30 * self.velocidad))  # Ajuste según velocidad

    def cerrar_video(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def toggle_pausa(self):
        self.paused = not self.paused
        self.boton_pausa.configure(text="Reanudar" if self.paused else "Pausar")

    def cambiar_velocidad(self, value):
        velocidades = {
            "0.5x": 0.5,
            "1x": 1.0,
            "1.5x": 1.5,
            "2x": 2.0
        }
        self.velocidad = velocidades.get(value, 1.0)

# Ejecutar ventana si se llama directamente
if __name__ == "__main__":
    app = customtkinter.CTk()
    app.withdraw()
    VentanaGrabaciones()
    app.mainloop()
